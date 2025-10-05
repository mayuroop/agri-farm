# Configuration file for the agricultural application

# Weather API configuration
weather_api_key = '49ac32c408fa46cc9bc112426240308'  # Your existing weather API key

# Model paths
disease_model_path = 'models/plant_disease_model.pth'
crop_recommendation_model_path = 'models/RandomForest.pkl'

# Data paths
fertilizer_data_path = 'Data/fertilizer.csv'

# Flask configuration
SECRET_KEY = '8e388483h8fqeubb'  # Your existing secret key

# Database configuration (if needed)
# MONGODB_URI = "mongodb+srv://admin:admin@app.1y5xkze.mongodb.net/?retryWrites=true&w=majority"

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Crop recommendation parameters
CROP_PARAMETERS = {
    'nitrogen': {'min': 0, 'max': 300, 'unit': 'ppm'},
    'phosphorous': {'min': 0, 'max': 150, 'unit': 'ppm'},
    'potassium': {'min': 0, 'max': 250, 'unit': 'ppm'},
    'ph': {'min': 3.0, 'max': 12.0, 'unit': 'pH'},
    'rainfall': {'min': 0, 'max': 5000, 'unit': 'mm'},
    'temperature': {'min': -10, 'max': 50, 'unit': '°C'},
    'humidity': {'min': 0, 'max': 100, 'unit': '%'}
}
