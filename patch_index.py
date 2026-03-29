import re
import os

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Markup fix
content = content.replace("from flask import Flask, render_template, request, Markup", "from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify\nfrom markupsafe import Markup\nimport os")
content = content.replace("from flask import Flask, render_template, request, redirect, url_for , session ,flash, jsonify, Markup", "from flask import Flask, render_template, request, redirect, url_for , session ,flash, jsonify\nfrom markupsafe import Markup\nimport os")

# 2. Add imports
imports = """
from utils.disease_detection import predict_disease
from utils.explainable_ai import explain_prediction
import base64
import io
import traceback
"""
content = content.replace("import config\n", "import config\n" + imports)

# 3. Add _BASE_DIR
content = content.replace("app = Flask(__name__)", "app = Flask(__name__)\n_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\nUPLOAD_FOLDER = os.path.join(_BASE_DIR, 'api', 'static', 'uploads')\nos.makedirs(UPLOAD_FOLDER, exist_ok=True)")

# 4. Modify get_ml_crop_recommendation
ml_func = """def get_ml_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    global crop_recommendation_model
    if crop_recommendation_model is not None and not isinstance(crop_recommendation_model, MockRandomForestModel):
        try:
            import numpy as np
            feature_list = [n, p, k, temperature, humidity, ph, rainfall]
            single_pred = np.array(feature_list).reshape(1, -1)
            prediction = crop_recommendation_model.predict(single_pred)
            raw_pred = prediction[0]
            
            crop_dict = {
                1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut",
                6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon",
                10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
                14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean",
                18: "Mothbeans", 19: "Pigeonpeas", 20: "Kidneybeans",
                21: "Chickpea", 22: "Coffee"
            }
            if isinstance(raw_pred, (int, np.integer)):
                crop_name = crop_dict.get(int(raw_pred), str(raw_pred))
            else:
                crop_name = str(raw_pred).capitalize()
            
            conf = 87.0
            try:
                proba = crop_recommendation_model.predict_proba(single_pred)
                conf = float(np.max(proba)) * 100
            except Exception as e:
                print("Proba failed:", e)
                
            confidence = 'High' if conf >= 80 else 'Medium' if conf >= 50 else 'Low'
            return [{'crop': crop_name, 'score': round(conf, 1), 'confidence': confidence}]
        except Exception as e:
            print(f"ML Model failed: {e}")
    
    return get_gemini_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)
"""
content = re.sub(r'def get_ml_crop_recommendation.*?return get_gemini_crop_recommendation\(n, p, k, temperature, humidity, ph, rainfall\)', ml_func, content, flags=re.DOTALL)

# 5. Fix fertilizer csv
content = content.replace("df = pd.read_csv('../Data/fertilizer.csv')", "df = pd.read_csv(os.path.join(_BASE_DIR, 'Data', 'fertilizer.csv'))")

# 6. Add routes before if __name__ == '__main__':
routes = """
@app.route('/disease-page')
def disease_page():
    if 'username' not in session:
        flash('You must be logged in to access Disease Detection.')
        return redirect(url_for('login'))
    return render_template('disease.html')

@app.route('/disease-detect', methods=['POST'])
def disease_detect():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    
    model_path = os.path.join(_BASE_DIR, 'models', 'plant_disease_model.pth')
    res = predict_disease(file, model_path)
    return jsonify(res)

@app.route('/api/explain-crop', methods=['POST'])
def explain_crop_api():
    try:
        data = request.json
        features = data.get('features', {})
        feature_values = [
            float(features.get('N', 0)),
            float(features.get('P', 0)),
            float(features.get('K', 0)),
            float(features.get('temperature', 0)),
            float(features.get('humidity', 0)),
            float(features.get('ph', 0)),
            float(features.get('rainfall', 0))
        ]
        feature_names = ['Nitrogen', 'Phosphorus', 'Potassium', 'Temperature', 'Humidity', 'pH', 'Rainfall']
        
        global crop_recommendation_model
        if crop_recommendation_model is None or isinstance(crop_recommendation_model, MockRandomForestModel):
            return jsonify({'success': False, 'error': 'Real model not loaded'})
            
        res = explain_prediction(crop_recommendation_model, feature_values, feature_names)
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

"""
content = content.replace("if __name__ == '__main__':", routes + "\nif __name__ == '__main__':")

# Fix scaler loading block
content = re.sub(r'standscaler_path =.*?minmax_scaler = None', 'print("Scalers removed")', content, flags=re.DOTALL)

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Patch applied successfully")
