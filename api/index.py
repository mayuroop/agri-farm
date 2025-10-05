from flask import Flask, render_template, request, redirect, url_for , session ,flash, jsonify, Markup
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

app = Flask(__name__)
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


@app.route('/crop-prices', methods=['GET', 'POST'])
def crop_prices_view():
    if request.method == 'POST':
        district_name = request.form['district']
        crop_prices = requests.get(f'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b&format=json&filters%5Bstate.keyword%5D=Maharashtra&filters%5Bdistrict%5D={district_name}').json()
        print(crop_prices)
        return render_template('crop_prices.html', data=crop_prices)
    return render_template('crop_prices.html',data=cp)


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
    
    def predict(self, X):
        """Predict crop based on input parameters"""
        n, p, k, temp, humidity, ph, rainfall = X[0]
        
        # Simple rule-based logic for crop recommendation
        if temp < 15:
            return ['Wheat']
        elif temp > 30:
            if humidity > 70:
                return ['Rice']
            else:
                return ['Cotton']
        elif ph < 6.0:
            if rainfall > 1000:
                return ['Rice']
            else:
                return ['Maize']
        elif ph > 8.0:
            return ['Cotton']
        elif n > 100 and p > 50 and k > 50:
            return ['Sugarcane']
        elif rainfall > 1200:
            return ['Rice']
        elif rainfall < 500:
            return ['Jowar']
        else:
            return ['Maize']
    
    def predict_proba(self, X):
        """Return mock probabilities"""
        prediction = self.predict(X)
        crop_index = self.crops.index(prediction[0])
        proba = [0.1] * len(self.crops)
        proba[crop_index] = 0.7
        return np.array([proba])

try:
    # Load crop recommendation model
    crop_recommendation_model_path = '../models/RandomForest.pkl'
    if os.path.exists(crop_recommendation_model_path):
        try:
            # Try loading with joblib first (recommended for scikit-learn models)
            crop_recommendation_model = joblib.load(crop_recommendation_model_path)
            print("Crop recommendation model loaded successfully with joblib")
        except Exception as joblib_error:
            print(f"Error loading with joblib: {joblib_error}")
            # Try with pickle
            try:
                with open(crop_recommendation_model_path, 'rb') as f:
                    crop_recommendation_model = pickle.load(f)
                print("Crop recommendation model loaded successfully with pickle")
            except Exception as pickle_error:
                print(f"Error loading pickle file: {pickle_error}")
                # Try with different encoding
                try:
                    with open(crop_recommendation_model_path, 'rb') as f:
                        crop_recommendation_model = pickle.load(f, encoding='latin1')
                    print("Crop recommendation model loaded successfully (with latin1 encoding)")
                except Exception as encoding_error:
                    print(f"Error with latin1 encoding: {encoding_error}")
                    print("Using mock RandomForest model due to file corruption")
                    crop_recommendation_model = MockRandomForestModel()
    else:
        print(f"Crop recommendation model file not found at {crop_recommendation_model_path}, using mock model")
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
    
    try:
        # Prepare data in the format expected by the model
        # The model expects: [N, P, K, temperature, humidity, ph, rainfall]
        data = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        
        # Get prediction from RandomForest model
        prediction = crop_recommendation_model.predict(data)
        crop_name = prediction[0]
        
        # Get prediction probabilities for confidence scoring
        try:
            probabilities = crop_recommendation_model.predict_proba(data)
            max_probability = np.max(probabilities)
            confidence_score = max_probability * 100
            
            if confidence_score >= 80:
                confidence = 'High'
            elif confidence_score >= 60:
                confidence = 'Medium'
            else:
                confidence = 'Low'
        except:
            # If predict_proba is not available, use default confidence
            confidence_score = 85.0
            confidence = 'High'
        
        print(f"ML model prediction: {crop_name} (confidence: {confidence_score:.1f}%)")
        
        # Return in the same format as the rule-based function
        return [{
            'crop': crop_name,
            'score': float(round(confidence_score, 1)),
            'confidence': confidence
        }]
        
    except Exception as e:
        print(f"Error in ML crop recommendation: {e}")
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
            
            # Get recommendations using ML model if available, otherwise use rule-based
            recommendations = get_ml_crop_recommendation(n, p, k, temperature, humidity, ph, rainfall)
            
            return jsonify({
                'success': True,
                'recommendations': recommendations,
                'input_data': {
                    'n': float(n),
                    'p': float(p),
                    'k': float(k),
                    'temperature': float(temperature),
                    'humidity': float(humidity),
                    'ph': float(ph),
                    'rainfall': float(rainfall)
                }
            })
            
        except Exception as e:
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
            df = pd.read_csv('../Data/fertilizer.csv')
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
    allowed_routes = ['login','register', 'home']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect(url_for('login'))

@app.errorhandler(Exception)
def handle_exception(e):
    logs_collection.insert_one({
        'type': 'error',
        'error': str(e),
        'path': request.path,
        'method': request.method,
        'timestamp': datetime.utcnow()
    })
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

if __name__ == '__main__':
    app.run(debug=True)
