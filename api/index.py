from flask import Flask, render_template, request, redirect, url_for , session ,flash, jsonify
from markupsafe import Markup
import os
import requests , json
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import re
import numpy as np
import pandas as pd
import pickle
import joblib
import os
import sys
import google.generativeai as genai

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.fertilizer import fertilizer_dic
import config

from utils.disease_detection import predict_disease
from utils.explainable_ai import explain_crop
import base64
import io
import traceback

from utils.disease_detection import predict_disease
from utils.explainable_ai import explain_crop
import base64
import io
import traceback

app = Flask(__name__)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(_BASE_DIR, 'api', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(_BASE_DIR, 'api', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.secret_key = '8e388483h8fqeubb' 

client = MongoClient("mongodb+srv://admin:admin@app.1y5xkze.mongodb.net/?retryWrites=true&w=majority")
db = client['agriculture']
orders_collection = db['orders']
items_collection = db['items']
user_collection = db['users']
logs_collection = db['logs']
feedback_collection = db['feedback']

cp = {
    'Wheat': {
        'Mumbai': 2200,
        'Pune': 2150,
        'Nagpur': 2100,
        'Aurangabad': 2125,
        'Nashik': 2175,
    },
    'Rice': {
        'Mumbai': 2800,
        'Pune': 2750,
        'Nagpur': 2700,
        'Aurangabad': 2725,
        'Nashik': 2775,
    },
    'Sugarcane': {
        'Mumbai': 3500,
        'Pune': 3400,
        'Nagpur': 3300,
        'Aurangabad': 3350,
        'Nashik': 3450,
    },
    'Cotton': {
        'Mumbai': 4500,
        'Pune': 4400,
        'Nagpur': 4300,
        'Aurangabad': 4350,
        'Nashik': 4450,
    },
    'Soybean': {
        'Mumbai': 3000,
        'Pune': 2900,
        'Nagpur': 2800,
        'Aurangabad': 2850,
        'Nashik': 2950,
    },
    'Groundnut': {
        'Mumbai': 2700,
        'Pune': 2600,
        'Nagpur': 2500,
        'Aurangabad': 2550,
        'Nashik': 2650,
    },
    'Jowar': {
        'Mumbai': 2300,
        'Pune': 2200,
        'Nagpur': 2100,
        'Aurangabad': 2150,
        'Nashik': 2250,
    },
    'Maize': {
        'Mumbai': 2600,
        'Pune': 2500,
        'Nagpur': 2400,
        'Aurangabad': 2450,
        'Nashik': 2550,
    },
}
users = {
    'admin@gmail.com': {'password': 'u', 'name': 'Mayur','role':'admin'},
    'user@gmail.com': {'password': 'u', 'name': 'Neo','role':'use'},
    'mayurxsu@gmail.com': {'password': 'Agri@123', 'name': 'xeneo','role':'use'}
}
marketplace_items = [
    {
        'name': 'Organic Tomatoes',
        'description': 'Fresh organic tomatoes from local farms.',
        'price': 50.00,
        'image_url': 'https://www.garden-products.co.uk/wp-content/uploads/2024/02/Tomatoes-scaled.jpeg'
    },
    {
        'name': ' Bannana',
        'description': 'High-quality Bannana',
        'price': 40.00,
        'image_url': 'https://cms-article.forbesindia.com/media/images/2022/Sep/img_193773_banana.jpg'
    },
    {
        'name': 'Green Spinach',
        'description': 'Freshly picked spinach, rich in vitamins.',
        'price': 30.00,
        'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTR8fHNwaW5hY2h8ZW58MHx8MHx8fDA%3D'
    }
]

@app.route('/')
def home():
    return render_template('index.html')

AGMARKET_API_KEY = '579b464db66ec23bdd000001bf789eaa575c446474b491404b9d2864'

@app.route('/crop-prices', methods=['GET', 'POST'])
def crop_prices_view():
    today = datetime.now().strftime('%Y-%m-%d')
    today= '2026-03-26' # e.g. 2026-03-27
    district = ''
    data = None

    if request.method == 'POST':
        district = request.form.get('district', '').strip()
        url = (
            f'https://api.data.gov.in/resource/35985678-0d79-46b4-9ed6-6f13308a1d24'
            f'?api-key={AGMARKET_API_KEY}'
            f'&format=json'
            f'&limit=100'
            f'&filters%5BState%5D=Maharashtra'
            f'&filters%5BDistrict%5D={district}'
            f'&filters%5BArrival_Date%5D={today}'
        )
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
        except Exception as e:
            data = {'error': str(e), 'records': [], 'total': 0}

    return render_template('crop_prices.html',
                           data=data,
                           district=district,
                           today=today)


@app.route('/marketplace', methods=['GET'])
def marketplace_view():
    if 'username' not in session:
        flash('You must be logged in to view the marketplace.')
        return redirect(url_for('login'))
    
    items = list(items_collection.find())
    if session.get('role') == 'admin':
        return render_template('marketplace.html', items=items)
    else:
        return render_template('marketplace2.html', items=items)


@app.route('/add-item', methods=['POST'])
def add_item():
    if session.get('role') != 'admin':
        return 'You are not an admin', 403
    item = request.form['name']
    location = request.form['location']
    description = request.form['description']
    price = float(request.form['price'])
    iid = request.form['iid']
    image_url = request.form.get('image_url', '') 
    item_doc = {
        'name': item,
        'iid': iid,
        'location': location,
        'description': description,
        'price': price,
        'image_url': image_url
    }
    items_collection.insert_one(item_doc)
    logs_collection.insert_one({
        'type': 'admin_action',
        'action': 'add_item',
        'admin': session.get('username'),
        'item': item_doc,
        'timestamp': datetime.utcnow()
    })
    return redirect(url_for('marketplace_view'))

@app.route('/delete_item/<item_id>', methods=['POST'])
def delete_item(item_id):
    deleted = items_collection.find_one_and_delete({"iid": item_id})
    logs_collection.insert_one({
        'type': 'admin_action',
        'action': 'delete_item',
        'admin': session.get('username'),
        'item_id': item_id,
        'deleted_item': deleted,
        'timestamp': datetime.utcnow()
    })
    return redirect(url_for('marketplace_view'))

weather_api_key = '49ac32c408fa46cc9bc112426240308'
weather_base_url = 'http://api.weatherapi.com/v1/forecast.json'

# Gemini API Configuration
GEMINI_API_KEY = 'AIzaSyB2JMfq0VwAoUL3v3coyqRuevOwCgL0I9U'  # Free hardcoded API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialize ML models
crop_recommendation_model = None

# Create a mock RandomForest model since the original file is corrupted
class MockRandomForestModel:
    """Mock RandomForest model that provides intelligent crop recommendations"""
    
    def __init__(self):
        self.crops = ['Rice', 'Wheat', 'Maize', 'Sugarcane', 'Cotton', 'Soybean', 'Groundnut', 'Jowar']
        self.feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    
    def predict(self, X):
        """Predict crop based on input parameters"""
        n, p, k, temp, humidity, ph, rainfall = X[0]
        
        # More sophisticated rule-based logic for crop recommendation
        scores = {}
        
        # Rice scoring
        rice_score = 0
        if 20 <= temp <= 35: rice_score += 2
        if 70 <= humidity <= 90: rice_score += 2
        if 5.5 <= ph <= 7.0: rice_score += 1
        if 1000 <= rainfall <= 2500: rice_score += 2
        if 20 <= n <= 120: rice_score += 1
        if 10 <= p <= 50: rice_score += 1
        if 20 <= k <= 100: rice_score += 1
        scores['Rice'] = rice_score
        
        # Wheat scoring
        wheat_score = 0
        if 15 <= temp <= 25: wheat_score += 2
        if 40 <= humidity <= 70: wheat_score += 2
        if 6.0 <= ph <= 7.5: wheat_score += 1
        if 500 <= rainfall <= 1000: wheat_score += 2
        if 50 <= n <= 120: wheat_score += 1
        if 20 <= p <= 60: wheat_score += 1
        if 30 <= k <= 80: wheat_score += 1
        scores['Wheat'] = wheat_score
        
        # Maize scoring
        maize_score = 0
        if 18 <= temp <= 30: maize_score += 2
        if 50 <= humidity <= 80: maize_score += 2
        if 5.5 <= ph <= 7.5: maize_score += 1
        if 600 <= rainfall <= 1200: maize_score += 2
        if 60 <= n <= 150: maize_score += 1
        if 20 <= p <= 80: maize_score += 1
        if 40 <= k <= 120: maize_score += 1
        scores['Maize'] = maize_score
        
        # Sugarcane scoring
        sugarcane_score = 0
        if 20 <= temp <= 35: sugarcane_score += 2
        if 60 <= humidity <= 85: sugarcane_score += 2
        if 6.0 <= ph <= 7.5: sugarcane_score += 1
        if 1000 <= rainfall <= 2000: sugarcane_score += 2
        if 80 <= n <= 200: sugarcane_score += 1
        if 30 <= p <= 100: sugarcane_score += 1
        if 60 <= k <= 150: sugarcane_score += 1
        scores['Sugarcane'] = sugarcane_score
        
        # Cotton scoring
        cotton_score = 0
        if 20 <= temp <= 35: cotton_score += 2
        if 40 <= humidity <= 80: cotton_score += 2
        if 5.5 <= ph <= 8.0: cotton_score += 1
        if 500 <= rainfall <= 1200: cotton_score += 2
        if 40 <= n <= 120: cotton_score += 1
        if 15 <= p <= 60: cotton_score += 1
        if 30 <= k <= 100: cotton_score += 1
        scores['Cotton'] = cotton_score
        
        # Soybean scoring
        soybean_score = 0
        if 15 <= temp <= 30: soybean_score += 2
        if 50 <= humidity <= 80: soybean_score += 2
        if 6.0 <= ph <= 7.0: soybean_score += 1
        if 600 <= rainfall <= 1000: soybean_score += 2
        if 30 <= n <= 100: soybean_score += 1
        if 15 <= p <= 50: soybean_score += 1
        if 20 <= k <= 80: soybean_score += 1
        scores['Soybean'] = soybean_score
        
        # Groundnut scoring
        groundnut_score = 0
        if 20 <= temp <= 30: groundnut_score += 2
        if 50 <= humidity <= 80: groundnut_score += 2
        if 5.5 <= ph <= 7.0: groundnut_score += 1
        if 500 <= rainfall <= 1000: groundnut_score += 2
        if 20 <= n <= 80: groundnut_score += 1
        if 10 <= p <= 40: groundnut_score += 1
        if 20 <= k <= 60: groundnut_score += 1
        scores['Groundnut'] = groundnut_score
        
        # Jowar scoring
        jowar_score = 0
        if 20 <= temp <= 35: jowar_score += 2
        if 40 <= humidity <= 70: jowar_score += 2
        if 6.0 <= ph <= 8.0: jowar_score += 1
        if 400 <= rainfall <= 800: jowar_score += 2
        if 30 <= n <= 80: jowar_score += 1
        if 15 <= p <= 40: jowar_score += 1
        if 20 <= k <= 60: jowar_score += 1
        scores['Jowar'] = jowar_score
        
        # Return the crop with highest score
        best_crop = max(scores, key=scores.get)
        return [best_crop]
    
    def predict_proba(self, X):
        """Return mock probabilities based on scoring"""
        prediction = self.predict(X)
        crop_index = self.crops.index(prediction[0])
        proba = [0.05] * len(self.crops)  # Base probability for all crops
        proba[crop_index] = 0.75  # Higher probability for predicted crop
        return np.array([proba])

try:
    # Load crop recommendation model
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Try loading new model first
    new_model_path = os.path.join(parent_dir, 'models', 'model.pkl')
    
    if os.path.exists(new_model_path):
        try:
            crop_recommendation_model = pickle.load(open(new_model_path, 'rb'))
            print("✅ New robust crop recommendation model loaded successfully!")
        except Exception as e:
            print(f"Error loading new model: {e}")
            crop_recommendation_model = MockRandomForestModel()
    else:
        print(f"Crop model not found at {new_model_path}, using mock")
        crop_recommendation_model = MockRandomForestModel()

except Exception as e:
    print(f"Error loading crop recommendation model: {e}")
    print("Using mock RandomForest model")
    crop_recommendation_model = MockRandomForestModel()

# Crop recommendation mapping based on soil and weather parameters
def get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    """
    Simple crop recommendation based on parameter ranges
    This is a rule-based approach that can be replaced with ML model
    """
    # Normalize parameters
    n = float(n)
    p = float(p)
    k = float(k)
    temperature = float(temperature)
    humidity = float(humidity)
    ph = float(ph)
    rainfall = float(rainfall)
    
    # Define crop requirements
    crops = {
        'Rice': {
            'n_range': (20, 120),
            'p_range': (10, 50),
            'k_range': (20, 100),
            'temp_range': (20, 35),
            'humidity_range': (70, 90),
            'ph_range': (5.5, 7.0),
            'rainfall_range': (1000, 2500)
        },
        'Wheat': {
            'n_range': (50, 120),
            'p_range': (20, 60),
            'k_range': (30, 80),
            'temp_range': (15, 25),
            'humidity_range': (40, 70),
            'ph_range': (6.0, 7.5),
            'rainfall_range': (500, 1000)
        },
        'Maize': {
            'n_range': (60, 150),
            'p_range': (20, 80),
            'k_range': (40, 120),
            'temp_range': (18, 30),
            'humidity_range': (50, 80),
            'ph_range': (5.5, 7.5),
            'rainfall_range': (600, 1200)
        },
        'Sugarcane': {
            'n_range': (80, 200),
            'p_range': (30, 100),
            'k_range': (60, 150),
            'temp_range': (20, 35),
            'humidity_range': (60, 85),
            'ph_range': (6.0, 7.5),
            'rainfall_range': (1000, 2000)
        },
        'Cotton': {
            'n_range': (40, 120),
            'p_range': (15, 60),
            'k_range': (30, 100),
            'temp_range': (20, 35),
            'humidity_range': (40, 80),
            'ph_range': (5.5, 8.0),
            'rainfall_range': (500, 1200)
        },
        'Soybean': {
            'n_range': (30, 100),
            'p_range': (15, 50),
            'k_range': (20, 80),
            'temp_range': (15, 30),
            'humidity_range': (50, 80),
            'ph_range': (6.0, 7.0),
            'rainfall_range': (600, 1000)
        },
        'Groundnut': {
            'n_range': (20, 80),
            'p_range': (10, 40),
            'k_range': (20, 60),
            'temp_range': (20, 30),
            'humidity_range': (50, 80),
            'ph_range': (5.5, 7.0),
            'rainfall_range': (500, 1000)
        },
        'Jowar': {
            'n_range': (30, 80),
            'p_range': (15, 40),
            'k_range': (20, 60),
            'temp_range': (20, 35),
            'humidity_range': (40, 70),
            'ph_range': (6.0, 8.0),
            'rainfall_range': (400, 800)
        }
    }
    
    # Calculate compatibility scores
    scores = {}
    for crop, requirements in crops.items():
        score = 0
        total_checks = 0
        
        # Check N
        if requirements['n_range'][0] <= n <= requirements['n_range'][1]:
            score += 1
        total_checks += 1
        
        # Check P
        if requirements['p_range'][0] <= p <= requirements['p_range'][1]:
            score += 1
        total_checks += 1
        
        # Check K
        if requirements['k_range'][0] <= k <= requirements['k_range'][1]:
            score += 1
        total_checks += 1
        
        # Check temperature
        if requirements['temp_range'][0] <= temperature <= requirements['temp_range'][1]:
            score += 1
        total_checks += 1
        
        # Check humidity
        if requirements['humidity_range'][0] <= humidity <= requirements['humidity_range'][1]:
            score += 1
        total_checks += 1
        
        # Check pH
        if requirements['ph_range'][0] <= ph <= requirements['ph_range'][1]:
            score += 1
        total_checks += 1
        
        # Check rainfall
        if requirements['rainfall_range'][0] <= rainfall <= requirements['rainfall_range'][1]:
            score += 1
        total_checks += 1
        
        scores[crop] = score / total_checks
    
    # Return top 3 recommendations
    sorted_crops = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    recommendations = []
    
    for crop, score in sorted_crops[:3]:
        recommendations.append({
            'crop': crop,
            'score': round(score * 100, 1),
            'confidence': 'High' if score > 0.7 else 'Medium' if score > 0.5 else 'Low'
        })
    
    return recommendations

def weather_fetch(city_name):
    """
    Fetch and returns the temperature and humidity of a city
    :params: city_name
    :return: temperature, humidity
    """
    api_key = weather_api_key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]
        temperature = round((y["temp"] - 273.15), 2)
        humidity = y["humidity"]
        return temperature, humidity
    else:
        return None


def get_ml_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall):
    """
    Get crop recommendation using the trained RandomForest ML model
    """
    if crop_recommendation_model is None:
        print("ML model not available, using rule-based fallback")
        return get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)
    
    # Mapping from integer label to crop name (matches the training dataset encoding)
    crop_dict = {
        1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut",
        6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon",
        10: "Watermelon", 11: "Grapes", 12: "Mango", 13: "Banana",
        14: "Pomegranate", 15: "Lentil", 16: "Blackgram", 17: "Mungbean",
        18: "Mothbeans", 19: "Pigeonpeas", 20: "Kidneybeans",
        21: "Chickpea", 22: "Coffee"
    }

    try:
        # Prepare data in the format expected by the model
        # The model expects: [N, P, K, temperature, humidity, ph, rainfall]
        data = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        
        # Get prediction from RandomForest model
        prediction = crop_recommendation_model.predict(data)
        raw_pred = prediction[0]

        # Decode integer label to crop name (model returns int64 labels)
        if isinstance(raw_pred, (int, np.integer)):
            crop_name = crop_dict.get(int(raw_pred), f"Crop-{int(raw_pred)}")
        else:
            crop_name = str(raw_pred).strip().capitalize()
        
        # Get prediction probabilities for confidence scoring
        try:
            probabilities = crop_recommendation_model.predict_proba(data)
            max_probability = np.max(probabilities)
            confidence_score = float(max_probability * 100)
            
            if confidence_score >= 80:
                confidence = 'High'
            elif confidence_score >= 60:
                confidence = 'Medium'
            else:
                confidence = 'Low'
        except Exception as proba_error:
            print(f"Error getting probabilities: {proba_error}")
            # If predict_proba is not available, use default confidence
            confidence_score = 85.0
            confidence = 'High'
        
        print(f"ML model prediction: {crop_name} (confidence: {confidence_score:.1f}%)")
        
        # Return in the same format as the rule-based function
        # All values are native Python types to ensure JSON serialization
        return [{
            'crop': str(crop_name),
            'score': float(round(confidence_score, 1)),
            'confidence': str(confidence)
        }]
        
    except Exception as e:
        print(f"Error in ML crop recommendation: {e}")
        print("Falling back to rule-based recommendation")
        return get_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)

def get_gemini_response(user_message):
    """
    Get response from Gemini AI for farmer queries
    """
    try:
        # Create the model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Create a comprehensive agricultural prompt
        prompt = f"""You are AgriBot, an expert agricultural assistant designed to help farmers with all aspects of farming and agriculture. You have deep knowledge of:

- Crop cultivation and plant care
- Soil health and fertility management
- Pest and disease identification and control
- Weather patterns and irrigation
- Fertilization and nutrient management
- Harvesting techniques and timing
- Sustainable farming practices
- Modern agricultural technology

Please provide helpful, practical, and actionable advice. Keep responses informative but concise. Use bullet points and clear structure when appropriate. Include specific tips and recommendations.

Farmer's question: {user_message}

Please provide a comprehensive answer that helps the farmer solve their problem or learn more about the topic."""

        # Generate response
        response = model.generate_content(prompt)
        
        # Return the generated text
        if response and response.text:
            return response.text
        else:
            return """I apologize, but I'm having trouble generating a response right now. Please try rephrasing your question or ask about a specific farming topic like:

- Crop cultivation techniques
- Soil health and testing
- Pest and disease management
- Irrigation and water management
- Fertilization schedules
- Harvesting and storage

What specific farming challenge can I help you with?"""
            
    except Exception as e:
        print(f"Error with Gemini API: {e}")
        # Fallback to a general agricultural response
        return """I'm experiencing a technical difficulty connecting to my knowledge base right now. However, I can still help with general agricultural advice!

**Common Farming Topics I Can Help With:**

🌱 **Crop Management:** Planting, growing, and care techniques
🌍 **Soil Health:** Testing, improvement, and fertility management  
🐛 **Pest Control:** Identification and treatment strategies
🌤️ **Weather & Water:** Irrigation planning and drought management
🌿 **Fertilization:** NPK balance and organic amendments
🌾 **Harvesting:** Timing and proper storage techniques

Please try asking your question again, or be more specific about what farming challenge you're facing. I'm here to help make your farming more successful!"""

@app.route('/chatbot-page')
def chatbot_page():
    """Render the chatbot page"""
    return render_template('chatbot.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot queries using Gemini AI"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get response from Gemini
        bot_response = get_gemini_response(user_message)
        
        return jsonify({
            'success': True,
            'response': bot_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        print(f"Error in chatbot: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process your message. Please try again.',
            'response': 'I apologize for the technical difficulty. Please try again in a moment.'
        }), 500

@app.route('/weather', methods=['GET', 'POST'])
def weather():
    current_weather = None
    forecast_weather = None
    city = None
    if request.method == 'POST':
        city = request.form['city']
        current_weather_response = requests.get(f"{weather_base_url}/current.json?key={weather_api_key}&q={city}")
        forecast_weather_response = requests.get(f"{weather_base_url}/forecast.json?key={weather_api_key}&q={city}&days=2")
        # print(forecast_weather_response.json())
        print(current_weather_response.json())
        

        
        if current_weather_response.status_code == 200 and forecast_weather_response.status_code == 200:
            current_weather = current_weather_response.json()['current']
            forecast_weather = forecast_weather_response.json()['forecast']['forecastday'][1]
        else:
            flash('Unable to retrieve weather data. Please try again later.')
    
    return render_template('weather.html', current_weather=current_weather, forecast_weather=forecast_weather, city=city)

@app.route('/crop-recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    if request.method == 'POST':
        try:
            # Get form data
            n = request.form.get('n')
            p = request.form.get('p')
            k = request.form.get('k')
            temperature = request.form.get('temperature')
            humidity = request.form.get('humidity')
            ph = request.form.get('ph')
            rainfall = request.form.get('rainfall')
            
            # Validate inputs
            if not all([n, p, k, temperature, humidity, ph, rainfall]):
                return jsonify({'error': 'All fields are required'}), 400
            
            # Convert to float and validate ranges
            try:
                n = float(n)
                p = float(p)
                k = float(k)
                temperature = float(temperature)
                humidity = float(humidity)
                ph = float(ph)
                rainfall = float(rainfall)
            except ValueError:
                return jsonify({'error': 'All fields must be valid numbers'}), 400
            
            # Validate reasonable ranges
            if not (0 <= n <= 300) or not (0 <= p <= 200) or not (0 <= k <= 300):
                return jsonify({'error': 'N, P, K values must be between 0-300, 0-200, 0-300 respectively'}), 400
            
            if not (-10 <= temperature <= 50):
                return jsonify({'error': 'Temperature must be between -10°C and 50°C'}), 400
            
            if not (0 <= humidity <= 100):
                return jsonify({'error': 'Humidity must be between 0% and 100%'}), 400
            
            if not (0 <= ph <= 14):
                return jsonify({'error': 'pH must be between 0 and 14'}), 400
            
            if not (0 <= rainfall <= 5000):
                return jsonify({'error': 'Rainfall must be between 0 and 5000 mm'}), 400
            
            # Get recommendations using ML model if available, otherwise use rule-based
            recommendations = get_ml_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)
            
            # Determine model status
            model_status = "ML Model" if not isinstance(crop_recommendation_model, MockRandomForestModel) else "Rule-based Fallback"
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'model_status': model_status,
                'input_data': {
                    'n': n,
                    'p': p,
                    'k': k,
                    'temperature': temperature,
                    'humidity': humidity,
                    'ph': ph,
                    'rainfall': rainfall
                }
            })
            
        except Exception as e:
            print(f"Error in crop recommendation: {e}")
            return jsonify({'error': f'Error processing recommendation: {str(e)}'}), 500
    
    return render_template('index.html')


@app.route('/fertilizer-recommendation')
def fertilizer_recommendation():
    """Render fertilizer recommendation page"""
    return render_template('fertilizer.html')

@app.route('/fertilizer-predict', methods=['POST'])
def fertilizer_predict():
    """Handle fertilizer recommendation"""
    try:
        crop_name = request.form.get('cropname')
        n = int(request.form.get('nitrogen'))
        p = int(request.form.get('phosphorous'))
        k = int(request.form.get('pottasium'))
        
        if not all([crop_name, n is not None, p is not None, k is not None]):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Load fertilizer data
        try:
            df = pd.read_csv(os.path.join(_BASE_DIR, 'Data', 'fertilizer.csv'))
            crop_data = df[df['Crop'] == crop_name]
            
            if crop_data.empty:
                return jsonify({'error': 'Crop not found in database'}), 400
            
            nr = crop_data['N'].iloc[0]
            pr = crop_data['P'].iloc[0]
            kr = crop_data['K'].iloc[0]
            
            # Calculate differences
            n_diff = nr - n
            p_diff = pr - p
            k_diff = kr - k
            
            # Find the nutrient with maximum deficiency
            temp = {abs(n_diff): "N", abs(p_diff): "P", abs(k_diff): "K"}
            max_value = temp[max(temp.keys())]
            
            if max_value == "N":
                if n_diff < 0:
                    key = 'NHigh'
                else:
                    key = "Nlow"
            elif max_value == "P":
                if p_diff < 0:
                    key = 'PHigh'
                else:
                    key = "Plow"
            else:
                if k_diff < 0:
                    key = 'KHigh'
                else:
                    key = "Klow"
            
            recommendation = fertilizer_dic.get(key, "Recommendation not available")
            
            return jsonify({
                'success': True,
                'recommendation': recommendation,
                'nutrient_analysis': {
                    'nitrogen': {'current': int(n), 'recommended': int(nr), 'difference': int(n_diff)},
                    'phosphorous': {'current': int(p), 'recommended': int(pr), 'difference': int(p_diff)},
                    'potassium': {'current': int(k), 'recommended': int(kr), 'difference': int(k_diff)}
                },
                'primary_deficiency': max_value
            })
            
        except FileNotFoundError:
            return jsonify({'error': 'Fertilizer data not found'}), 500
        except Exception as e:
            return jsonify({'error': f'Error processing fertilizer data: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/buy/<iid>', methods=['GET', 'POST'])
def buy_item(iid):
    def log_order(username, iid, status, reason=None):
        logs_collection.insert_one({
            'type': 'order',
            'username': username,
            'iid': iid,
            'status': status,
            'reason': reason,
            'timestamp': datetime.utcnow()
        })
    if 'username' not in session:
        log_order(None, iid, 'fail', 'User not logged in')
        flash('You must be logged in to buy an item.')
        return redirect(url_for('login'))
    if request.method == 'POST':
        address = request.form['address']
        phone = request.form['phone']
        item = items_collection.find_one({"iid": iid})
        if item:
            order = {
                'username': session['username'],
                'item': item,
                'address': address,
                'phone': phone,
                'status': 'Order Placed',
                'timestamp': datetime.utcnow()
            }
            result = orders_collection.insert_one(order)
            log_order(session['username'], iid, 'success')
            # Show confirmation page
            return render_template('buy_item.html', item=item, iid=iid, confirmation=True)
        else:
            log_order(session['username'], iid, 'fail', 'Item not found')
            flash('Item not found.')
        return redirect(url_for('marketplace_view'))
    item = items_collection.find_one({"iid": iid})
    return render_template('buy_item.html', item=item, iid=iid)

@app.route('/orders')
def view_orders():
    if 'username' not in session:
        flash('You must be logged in to view your orders.')
        return redirect(url_for('login'))

    user_orders = orders_collection.find({'username': session['username']}).sort('_id', -1)
    return render_template('orders.html', orders=user_orders)

@app.route('/admin')
def admin_orders():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You must be an admin to view this page.')
        return redirect(url_for('login'))

    all_orders = orders_collection.find()
    return render_template('admin_orders.html', orders=all_orders)

@app.route('/admin/mark_done/<order_id>')
def mark_done(order_id):
    if 'username' not in session or session.get('role') != 'admin':
        flash('You must be an admin to perform this action.')
        return redirect(url_for('login'))
    orders_collection.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': 'Done'}})
    logs_collection.insert_one({
        'type': 'admin_action',
        'action': 'mark_done',
        'admin': session.get('username'),
        'order_id': order_id,
        'timestamp': datetime.utcnow()
    })
    return redirect(url_for('admin_orders'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        flash('You must be an admin to view this page.')
        return redirect(url_for('login'))
    total_users = user_collection.count_documents({})
    total_items = items_collection.count_documents({})
    total_orders = orders_collection.count_documents({})
    total_registrations = logs_collection.count_documents({'type': 'registration'})
    failed_registrations = logs_collection.count_documents({'type': 'registration', 'status': 'fail'})
    total_logins = logs_collection.count_documents({'type': 'login'})
    failed_logins = logs_collection.count_documents({'type': 'login', 'status': 'fail'})
    total_orders_logged = logs_collection.count_documents({'type': 'order'})
    failed_orders = logs_collection.count_documents({'type': 'order', 'status': 'fail'})
    admin_actions = list(logs_collection.find({'type': 'admin_action'}).sort('timestamp', -1).limit(10))
    feedbacks = list(feedback_collection.find().sort('timestamp', -1).limit(10))
    return render_template('admin_dashboard.html',
        total_users=total_users,
        total_items=total_items,
        total_orders=total_orders,
        total_registrations=total_registrations,
        failed_registrations=failed_registrations,
        total_logins=total_logins,
        failed_logins=failed_logins,
        total_orders_logged=total_orders_logged,
        failed_orders=failed_orders,
        admin_actions=admin_actions,
        feedbacks=feedbacks
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    def log_registration(email, status, reason=None):
        logs_collection.insert_one({
            'type': 'registration',
            'email': email,
            'status': status,
            'reason': reason,
            'timestamp': datetime.utcnow()
        })

    if request.method == 'POST':
        usern = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Email format validation
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not email or not password or not usern:
            log_registration(email, 'fail', 'Missing required fields')
            return render_template('register.html', msg={'type': 'error', 'text': 'Missing required fields'})
        if not re.match(email_regex, email):
            log_registration(email, 'fail', 'Invalid email format')
            return render_template('register.html', msg={'type': 'error', 'text': 'Invalid email format'})
        if user_collection.find_one({'email': email}):
            log_registration(email, 'fail', 'User already exists')
            return render_template('register.html', msg={'type': 'error', 'text': 'User already exists'})
        # Password strength check
        if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            log_registration(email, 'fail', 'Password must be at least 8 characters and contain both letters and numbers')
            return render_template('register.html', msg={'type': 'error', 'text': 'Password must be at least 8 characters and contain both letters and numbers'})
        if password != confirm_password:
            log_registration(email, 'fail', 'Passwords do not match')
            return render_template('register.html', msg={'type': 'error', 'text': 'Passwords do not match'})
        user_data = {
            'name': usern,
            'email': email,
            'password': password,
            'role': 'use'
        }
        user_collection.insert_one(user_data)
        log_registration(email, 'success')
        return render_template('register.html', msg={'type': 'success', 'text': 'User registered successfully'})
    return render_template('register.html', msg={'type': 'info', 'text': 'hi'})


@app.route('/login', methods=['GET', 'POST'])
def login():
    def log_login(email, status, reason=None):
        logs_collection.insert_one({
            'type': 'login',
            'email': email,
            'status': status,
            'reason': reason,
            'timestamp': datetime.utcnow()
        })
    if 'username' in session:  # Check if user is already logged in
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = user_collection.find_one({'email': email})
        # Check for lockout
        lockout = False
        lockout_reason = None
        if user:
            recent_failed = list(logs_collection.find({
                'type': 'login',
                'email': email,
                'status': 'fail',
                'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=10)}
            }).sort('timestamp', -1).limit(5))
            if len(recent_failed) >= 5:
                lockout = True
                lockout_reason = 'Account locked due to too many failed login attempts. Try again after 10 minutes.'
        if lockout:
            log_login(email, 'fail', lockout_reason)
            return render_template('login.html', res=lockout_reason)
        if user and user['password'] == password:
            session['user'] = email
            session['username'] = user['name']
            session['role'] = user['role']
            log_login(email, 'success')
            return redirect(url_for('home'))
        else:
            log_login(email, 'fail', 'Invalid credentials')
            return render_template('login.html', res='Invalid credentials, please try again.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.before_request
def require_login():
    allowed_routes = ['login','register', 'home', 'crop_recommendation', 'fertilizer_predict',
                      'weather', 'chatbot', 'chatbot_page', 'crop_prices_view', 'feedback',
                      'explain_crop_api', 'yield_prediction', 'yield_prediction_api']  # API routes must not redirect to login HTML
    if 'user' not in session and request.endpoint not in allowed_routes:
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        return redirect(url_for('login'))

@app.errorhandler(Exception)
def handle_exception(e):
    try:
        logs_collection.insert_one({
            'type': 'error',
            'error': str(e),
            'path': request.path,
            'method': request.method,
            'timestamp': datetime.utcnow()
        })
    except Exception:
        pass
    # Return JSON for API routes so the browser doesn't receive HTML
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': str(e)}), 500
    return render_template('error.html', error=str(e)), 500

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        username = session.get('username', 'Anonymous')
        message = request.form.get('message')
        if not message:
            return render_template('feedback.html', msg='Please enter your feedback.')
        feedback_collection.insert_one({
            'username': username,
            'message': message,
            'timestamp': datetime.utcnow()
        })
        return render_template('feedback.html', msg='Feedback submitted!')
    return render_template('feedback.html', msg=None)


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
        data = request.get_json(force=True, silent=True) or {}
        features = data.get('features', {})
        prediction_val = data.get('prediction', 'Unknown')

        try:
            n           = float(features.get('N', 0))
            p           = float(features.get('P', 0))
            k           = float(features.get('K', 0))
            temperature = float(features.get('temperature', 0))
            humidity    = float(features.get('humidity', 0))
            ph          = float(features.get('ph', 0))
            rainfall    = float(features.get('rainfall', 0))
        except (TypeError, ValueError) as parse_err:
            return jsonify({'success': False, 'error': f'Invalid feature values: {parse_err}'}), 400

        global crop_recommendation_model
        if crop_recommendation_model is None or isinstance(crop_recommendation_model, MockRandomForestModel):
            return jsonify({'success': False, 'error': 'Real ML model not loaded — SHAP unavailable'})

        res = explain_crop(crop_recommendation_model, n, p, k, temperature, humidity, ph, rainfall, prediction_val)
        return jsonify(res)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500



# ═══════════════════════════════════════════════════════════════
#  CROP YIELD PREDICTION ENGINE (ICAR-calibrated agronomic model)
# ═══════════════════════════════════════════════════════════════

# Base yield (t/ha) — national average from GoI / ICAR data
CROP_BASE_YIELD = {
    'Rice':       3.5,  'Wheat':      3.2,  'Maize':      3.0,
    'Sugarcane': 70.0,  'Cotton':     1.8,  'Jute':       2.5,
    'Chickpea':   1.1,  'Lentil':     0.9,  'Blackgram':  0.75,
    'Mungbean':   0.8,  'Mothbeans':  0.6,  'Pigeonpeas': 0.85,
    'Kidneybeans':1.2,  'Banana':    35.0,  'Mango':     10.0,
    'Coconut':  10000,  'Papaya':    40.0,  'Orange':    12.0,
    'Grapes':   15.0,   'Watermelon':25.0,  'Muskmelon': 18.0,
    'Coffee':    0.9,
}
# Coconut is in nuts/ha — convert to t/ha for display: ≈ 6 t copra equivalent
COCONUT_COPRA_EQUIV = 6.0

# MSP / indicative market price (₹/tonne) — GoI 2023-24
CROP_PRICE_PER_TONNE = {
    'Rice':21830,'Wheat':22750,'Maize':20900,'Sugarcane':3400,
    'Cotton':66200,'Jute':50500,'Chickpea':54400,'Lentil':60000,
    'Blackgram':74000,'Mungbean':85580,'Mothbeans':55500,
    'Pigeonpeas':70000,'Kidneybeans':55000,'Banana':12000,
    'Mango':30000,'Coconut':10860,'Papaya':10000,'Orange':25000,
    'Grapes':60000,'Watermelon':8000,'Muskmelon':12000,'Coffee':80000,
}

# Optimal soil/climate ranges per crop (used for multiplier scoring)
CROP_OPTIMA = {
    'Rice':       dict(n=(80,120),  p=(40,60),  k=(40,60),  ph=(5.5,7.0), rain=(1000,2500), temp=(22,30)),
    'Wheat':      dict(n=(80,120),  p=(40,60),  k=(40,60),  ph=(6.0,7.5), rain=(450,900),  temp=(15,22)),
    'Maize':      dict(n=(100,150), p=(50,80),  k=(50,80),  ph=(5.8,7.0), rain=(600,1200), temp=(20,28)),
    'Sugarcane':  dict(n=(150,200), p=(60,100), k=(80,120), ph=(6.0,7.5), rain=(1000,1800),temp=(25,35)),
    'Cotton':     dict(n=(80,120),  p=(40,60),  k=(40,60),  ph=(6.0,8.0), rain=(600,1200), temp=(25,35)),
    'Jute':       dict(n=(60,100),  p=(30,60),  k=(30,60),  ph=(6.0,7.5), rain=(1200,2000),temp=(25,35)),
    'Chickpea':   dict(n=(20,40),   p=(40,60),  k=(20,40),  ph=(6.0,7.5), rain=(300,600),  temp=(15,25)),
    'Lentil':     dict(n=(20,40),   p=(30,50),  k=(20,40),  ph=(6.0,7.5), rain=(250,500),  temp=(12,22)),
    'Blackgram':  dict(n=(20,40),   p=(30,50),  k=(20,40),  ph=(6.0,7.5), rain=(400,700),  temp=(25,35)),
    'Mungbean':   dict(n=(20,40),   p=(30,50),  k=(20,40),  ph=(6.0,7.5), rain=(350,700),  temp=(25,35)),
    'Mothbeans':  dict(n=(10,30),   p=(20,40),  k=(10,30),  ph=(6.5,8.0), rain=(200,400),  temp=(28,38)),
    'Pigeonpeas': dict(n=(20,40),   p=(40,60),  k=(20,40),  ph=(6.0,7.5), rain=(600,1000), temp=(25,35)),
    'Kidneybeans':dict(n=(20,40),   p=(30,50),  k=(30,50),  ph=(6.0,7.0), rain=(300,600),  temp=(15,25)),
    'Banana':     dict(n=(150,200), p=(50,100), k=(150,250),ph=(5.5,7.0), rain=(900,1800), temp=(25,35)),
    'Mango':      dict(n=(100,150), p=(50,80),  k=(80,120), ph=(5.5,7.5), rain=(600,1200), temp=(24,35)),
    'Coconut':    dict(n=(100,150), p=(40,80),  k=(200,300),ph=(5.5,7.0), rain=(1000,2000),temp=(25,32)),
    'Papaya':     dict(n=(100,150), p=(50,80),  k=(80,120), ph=(6.0,7.0), rain=(800,1500), temp=(25,35)),
    'Orange':     dict(n=(80,120),  p=(30,60),  k=(80,120), ph=(6.0,7.5), rain=(600,1200), temp=(15,30)),
    'Grapes':     dict(n=(80,120),  p=(30,60),  k=(80,120), ph=(6.0,7.5), rain=(500,900),  temp=(20,30)),
    'Watermelon': dict(n=(80,120),  p=(30,60),  k=(60,100), ph=(6.0,7.5), rain=(400,700),  temp=(25,35)),
    'Muskmelon':  dict(n=(60,100),  p=(30,50),  k=(50,80),  ph=(6.0,7.5), rain=(400,700),  temp=(25,35)),
    'Coffee':     dict(n=(100,150), p=(30,60),  k=(80,120), ph=(5.5,6.5), rain=(1500,2500),temp=(18,28)),
}

IRRIGATION_MULT  = {'rainfed':0.80,'canal':1.05,'drip':1.18,'sprinkler':1.12,'borewell':1.08}
FERTILIZER_MULT  = {'none':0.70,'low':0.88,'medium':1.00,'high':1.15}
SEED_MULT        = {'local':0.80,'certified':1.00,'hybrid':1.18}

IMPROVEMENT_TIPS = {
    'soil_n': 'Nitrogen is suboptimal — apply urea/DAP in split doses at sowing and tillering/vegetative stage.',
    'soil_p': 'Phosphorus is below optimal — apply SSP or DAP as basal dose before sowing.',
    'soil_k': 'Potassium is low — apply MOP (Muriate of Potash) for better root health and drought tolerance.',
    'soil_ph_low': 'Soil pH is too acidic — apply agricultural lime (CaCO₃) at 2–4 t/ha to raise pH.',
    'soil_ph_high':'Soil pH is too alkaline — apply gypsum or sulphur to lower pH for better nutrient uptake.',
    'rainfall': 'Rainfall is outside the optimal range — consider supplemental irrigation or rainwater harvesting.',
    'temp': 'Temperature is not ideal — choose a heat/cold-tolerant variety and adjust sowing date accordingly.',
    'irrigation':'Upgrade from rain-fed to drip or sprinkler irrigation to potentially increase yield by 15–30%.',
    'fertilizer':'Switch to split/precision fertilizer application to reduce wastage and boost yield quality.',
    'seed': 'Upgrade to certified HYV or hybrid seeds — they yield 20–40% more than local varieties.',
    'general': 'Register for PM-KISAN, PMFBY crop insurance and eNAM digital market to secure income.',
}

def _range_score(val, lo, hi):
    """Return 0–100 score for how close val is to [lo, hi]."""
    if lo <= val <= hi:
        return 100.0
    mid  = (lo + hi) / 2
    span = (hi - lo) / 2 or 1
    dist = max(abs(val - lo), abs(val - hi))
    return max(0, round(100 - (dist / span) * 40, 1))

def _soil_multiplier(crop, n, p, k, ph):
    opt = CROP_OPTIMA.get(crop, {})
    scores = []
    if 'n'  in opt: scores.append(_range_score(n,  *opt['n']))
    if 'p'  in opt: scores.append(_range_score(p,  *opt['p']))
    if 'k'  in opt: scores.append(_range_score(k,  *opt['k']))
    if 'ph' in opt: scores.append(_range_score(ph, *opt['ph']))
    avg = sum(scores) / len(scores) if scores else 80
    return 0.70 + (avg / 100) * 0.35   # range 0.70 – 1.05

def _climate_multiplier(crop, rainfall, temperature):
    opt = CROP_OPTIMA.get(crop, {})
    s_r = _range_score(rainfall,    *opt.get('rain', (600, 1500)))
    s_t = _range_score(temperature, *opt.get('temp', (20,  32)))
    avg = (s_r + s_t) / 2
    return 0.72 + (avg / 100) * 0.33

def _build_tips(crop, n, p, k, ph, rainfall, temperature, irrigation, fertilizer_use, seed_quality):
    tips = []
    opt  = CROP_OPTIMA.get(crop, {})
    if opt:
        if n  < opt.get('n',  (0,300))[0]:  tips.append(IMPROVEMENT_TIPS['soil_n'])
        if p  < opt.get('p',  (0,150))[0]:  tips.append(IMPROVEMENT_TIPS['soil_p'])
        if k  < opt.get('k',  (0,250))[0]:  tips.append(IMPROVEMENT_TIPS['soil_k'])
        lo, hi = opt.get('ph',(6,7.5))
        if ph < lo: tips.append(IMPROVEMENT_TIPS['soil_ph_low'])
        if ph > hi: tips.append(IMPROVEMENT_TIPS['soil_ph_high'])
        r_lo, r_hi = opt.get('rain',(500,2000))
        if not (r_lo <= rainfall <= r_hi): tips.append(IMPROVEMENT_TIPS['rainfall'])
        t_lo, t_hi = opt.get('temp',(18,35))
        if not (t_lo <= temperature <= t_hi): tips.append(IMPROVEMENT_TIPS['temp'])
    if irrigation  == 'rainfed':  tips.append(IMPROVEMENT_TIPS['irrigation'])
    if fertilizer_use in ('none','low'): tips.append(IMPROVEMENT_TIPS['fertilizer'])
    if seed_quality == 'local':   tips.append(IMPROVEMENT_TIPS['seed'])
    tips.append(IMPROVEMENT_TIPS['general'])
    return list(dict.fromkeys(tips))[:6]  # deduplicate, max 6

def predict_yield(crop, area, season, state, n, p, k, ph,
                  rainfall, temperature, irrigation, fertilizer_use, seed_quality):
    base      = CROP_BASE_YIELD.get(crop)
    if base is None:
        return None, 'Crop not found in yield database'

    # Coconut: normalise nuts → copra-equivalent tonnes
    if crop == 'Coconut':
        base = COCONUT_COPRA_EQUIV

    soil_m  = _soil_multiplier(crop, n, p, k, ph)
    clim_m  = _climate_multiplier(crop, rainfall, temperature)
    irr_m   = IRRIGATION_MULT.get(irrigation, 1.0)
    fert_m  = FERTILIZER_MULT.get(fertilizer_use, 1.0)
    seed_m  = SEED_MULT.get(seed_quality, 1.0)

    yield_t_ha = round(base * soil_m * clim_m * irr_m * fert_m * seed_m, 2)
    total_t    = round(yield_t_ha * area, 2)
    price      = CROP_PRICE_PER_TONNE.get(crop, 20000)
    revenue    = int(total_t * price)

    # Quality grade
    nat_avg = base
    ratio   = yield_t_ha / nat_avg
    if   ratio >= 1.20: grade, grade_reason = 'A', 'Yield ≥ 120% of national average — excellent input management!'
    elif ratio >= 1.00: grade, grade_reason = 'B', 'Yield meets or exceeds national average — good practices in place.'
    elif ratio >= 0.80: grade, grade_reason = 'C', 'Yield is 80–100% of national average — moderate constraints detected.'
    else:               grade, grade_reason = 'D', 'Yield is below 80% of national average — significant limiting factors present.'

    vs_national = round((yield_t_ha - nat_avg) / nat_avg * 100, 1)

    # Factor scores for the bar chart
    opt = CROP_OPTIMA.get(crop, {})
    factors = [
        {'name': 'Soil Nitrogen',   'score': int(_range_score(n,  *opt.get('n',  (50,150))))},
        {'name': 'Soil Phosphorus', 'score': int(_range_score(p,  *opt.get('p',  (30,80))))},
        {'name': 'Soil Potassium',  'score': int(_range_score(k,  *opt.get('k',  (30,100))))},
        {'name': 'Soil pH',         'score': int(_range_score(ph, *opt.get('ph', (6.0,7.5))))},
        {'name': 'Rainfall',        'score': int(_range_score(rainfall,    *opt.get('rain',(600,1500))))},
        {'name': 'Temperature',     'score': int(_range_score(temperature, *opt.get('temp',(20,32))))},
        {'name': 'Irrigation',      'score': int(irr_m  * 95)},
        {'name': 'Fertilizer',      'score': int(fert_m * 95)},
        {'name': 'Seed Quality',    'score': int(seed_m * 95)},
    ]

    # 3-scenario forecast
    def _scenario(mult, label):
        y = round(yield_t_ha * mult, 2)
        t = round(y * area, 2)
        r = int(t * price)
        rat = y / nat_avg
        g = 'A' if rat>=1.2 else 'B' if rat>=1.0 else 'C' if rat>=0.8 else 'D'
        return {'scenario':label,'yield_t_ha':y,'total_yield_t':t,'revenue':r,'grade':g}

    scenarios = [
        _scenario(0.80, 'Pessimistic (-20%)'),
        _scenario(1.00, 'Base Estimate'),
        _scenario(1.20, 'Optimistic (+20%)'),
    ]

    tips = _build_tips(crop, n, p, k, ph, rainfall, temperature, irrigation, fertilizer_use, seed_quality)

    return {
        'success':          True,
        'crop':             crop,
        'area':             area,
        'yield_t_ha':       yield_t_ha,
        'total_yield_t':    total_t,
        'revenue':          revenue,
        'grade':            grade,
        'grade_reason':     grade_reason,
        'national_avg':     round(nat_avg, 2),
        'vs_national':      vs_national,
        'factors':          factors,
        'scenario_forecast':scenarios,
        'tips':             tips,
    }, None


@app.route('/yield-prediction')
def yield_prediction():
    return render_template('yield_prediction.html')


@app.route('/api/yield-prediction', methods=['POST'])
def yield_prediction_api():
    try:
        d = request.get_json(force=True, silent=True) or {}
        crop           = str(d.get('crop', '')).strip()
        area           = float(d.get('area', 1))
        season         = str(d.get('season', ''))
        state          = str(d.get('state', ''))
        n              = float(d.get('n', 60))
        p              = float(d.get('p', 30))
        k              = float(d.get('k', 40))
        ph             = float(d.get('ph', 6.5))
        rainfall       = float(d.get('rainfall', 800))
        temperature    = float(d.get('temperature', 25))
        irrigation     = str(d.get('irrigation', 'canal'))
        fertilizer_use = str(d.get('fertilizer_use', 'medium'))
        seed_quality   = str(d.get('seed_quality', 'certified'))

        if not crop:
            return jsonify({'success': False, 'error': 'Please select a crop'}), 400
        if area <= 0:
            return jsonify({'success': False, 'error': 'Area must be greater than 0'}), 400

        result, err = predict_yield(crop, area, season, state, n, p, k, ph,
                                    rainfall, temperature, irrigation, fertilizer_use, seed_quality)
        if err:
            return jsonify({'success': False, 'error': err}), 400
        return jsonify(result)

    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'error': f'Invalid input: {e}'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
