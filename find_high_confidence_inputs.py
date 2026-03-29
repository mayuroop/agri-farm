"""
Find High Confidence Inputs for Multiple Crops
This script generates and tests inputs to find high confidence predictions for at least 10 crops
"""

import numpy as np
import joblib
import pandas as pd

# Load the model
model_path = 'models/RandomForest.pkl'
model = joblib.load(model_path)

print("="*80)
print("SEARCHING FOR HIGH CONFIDENCE INPUTS FOR 10+ CROPS")
print("="*80)
print()

# Get all crop classes
all_crops = model.classes_
print(f"Total crops in model: {len(all_crops)}")
print()

# Define typical ranges for each crop based on agricultural knowledge
crop_profiles = {
    'rice': [
        [90, 42, 43, 25, 82, 6.5, 202],
        [85, 45, 40, 23, 85, 6.3, 220],
        [95, 40, 45, 24, 80, 6.7, 210],
    ],
    'maize': [
        [100, 20, 18, 22, 68, 6.3, 60],
        [95, 18, 20, 21, 65, 6.4, 55],
        [105, 22, 17, 23, 70, 6.2, 65],
    ],
    'wheat': [
        [80, 40, 50, 18, 50, 6.8, 600],
        [75, 45, 55, 17, 48, 7.0, 580],
        [85, 42, 52, 19, 52, 6.9, 620],
    ],
    'cotton': [
        [100, 40, 40, 28, 60, 6.5, 800],
        [95, 38, 42, 27, 58, 6.6, 750],
        [105, 42, 38, 29, 62, 6.4, 820],
    ],
    'jute': [
        [80, 45, 40, 27, 80, 6.5, 1800],
        [85, 42, 38, 26, 82, 6.4, 1750],
        [78, 48, 42, 28, 78, 6.6, 1850],
    ],
    'coconut': [
        [20, 10, 30, 27, 90, 6.0, 1800],
        [22, 12, 28, 28, 88, 5.9, 1750],
        [18, 11, 32, 26, 92, 6.1, 1820],
    ],
    'coffee': [
        [100, 20, 30, 24, 70, 6.0, 1400],
        [95, 22, 28, 23, 72, 5.9, 1380],
        [105, 18, 32, 25, 68, 6.1, 1420],
    ],
    'chickpea': [
        [40, 60, 80, 18, 20, 7.5, 85],
        [38, 58, 82, 17, 22, 7.4, 80],
        [42, 62, 78, 19, 18, 7.6, 90],
    ],
    'kidneybeans': [
        [20, 60, 20, 20, 25, 5.5, 130],
        [22, 58, 22, 19, 23, 5.6, 125],
        [18, 62, 18, 21, 27, 5.4, 135],
    ],
    'pigeonpeas': [
        [20, 60, 20, 27, 50, 6.0, 900],
        [22, 58, 22, 26, 48, 6.1, 880],
        [18, 62, 18, 28, 52, 5.9, 920],
    ],
    'mothbeans': [
        [20, 40, 20, 28, 65, 6.5, 50],
        [22, 38, 22, 27, 63, 6.6, 48],
        [18, 42, 18, 29, 67, 6.4, 52],
    ],
    'mungbean': [
        [20, 40, 20, 28, 80, 6.5, 900],
        [22, 38, 22, 27, 82, 6.4, 880],
        [18, 42, 18, 29, 78, 6.6, 920],
    ],
    'blackgram': [
        [40, 60, 20, 28, 65, 7.0, 900],
        [38, 58, 22, 27, 63, 7.1, 880],
        [42, 62, 18, 29, 67, 6.9, 920],
    ],
    'lentil': [
        [20, 60, 20, 22, 65, 6.5, 65],
        [22, 58, 22, 21, 63, 6.6, 62],
        [18, 62, 18, 23, 67, 6.4, 68],
    ],
    'pomegranate': [
        [20, 10, 40, 22, 90, 6.5, 110],
        [22, 12, 38, 21, 88, 6.6, 105],
        [18, 11, 42, 23, 92, 6.4, 115],
    ],
    'banana': [
        [100, 75, 50, 28, 80, 6.5, 1200],
        [95, 78, 48, 27, 82, 6.4, 1180],
        [105, 72, 52, 29, 78, 6.6, 1220],
    ],
    'mango': [
        [20, 20, 30, 28, 60, 6.5, 1100],
        [22, 18, 32, 27, 58, 6.6, 1080],
        [18, 22, 28, 29, 62, 6.4, 1120],
    ],
    'grapes': [
        [20, 125, 200, 25, 80, 6.0, 200],
        [22, 120, 195, 24, 82, 5.9, 195],
        [18, 130, 205, 26, 78, 6.1, 205],
    ],
    'watermelon': [
        [100, 10, 50, 25, 85, 6.5, 50],
        [95, 12, 48, 24, 87, 6.4, 48],
        [105, 11, 52, 26, 83, 6.6, 52],
    ],
    'muskmelon': [
        [100, 10, 50, 28, 90, 6.5, 25],
        [95, 12, 48, 27, 88, 6.6, 23],
        [105, 11, 52, 29, 92, 6.4, 27],
    ],
    'apple': [
        [20, 125, 200, 22, 90, 6.0, 1200],
        [22, 120, 195, 21, 92, 5.9, 1180],
        [18, 130, 205, 23, 88, 6.1, 1220],
    ],
    'orange': [
        [20, 10, 10, 22, 90, 6.5, 1100],
        [22, 12, 12, 21, 88, 6.6, 1080],
        [18, 11, 11, 23, 92, 6.4, 1120],
    ],
    'papaya': [
        [50, 50, 50, 28, 90, 6.5, 1200],
        [48, 52, 48, 27, 88, 6.6, 1180],
        [52, 48, 52, 29, 92, 6.4, 1220],
    ],
}

# Test all inputs and find high confidence ones
high_confidence_results = []

for crop_name, test_inputs in crop_profiles.items():
    best_confidence = 0
    best_input = None
    best_prediction = None
    
    for input_values in test_inputs:
        X = np.array([input_values])
        
        try:
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            max_prob_index = np.argmax(probabilities)
            confidence = probabilities[max_prob_index] * 100
            
            # Check if this is the best for this crop
            if confidence > best_confidence:
                best_confidence = confidence
                best_input = input_values
                best_prediction = prediction
        except:
            continue
    
    # Store result if confidence is reasonable
    if best_confidence > 0:
        high_confidence_results.append({
            'target_crop': crop_name,
            'predicted_crop': best_prediction,
            'confidence': best_confidence,
            'input': best_input,
            'match': '✅' if best_prediction.lower() == crop_name.lower() else '❌'
        })

# Sort by confidence (descending)
high_confidence_results.sort(key=lambda x: x['confidence'], reverse=True)

# Display results
print("\n" + "="*80)
print("HIGH CONFIDENCE PREDICTIONS FOUND")
print("="*80)
print()

count = 0
for i, result in enumerate(high_confidence_results[:20], 1):  # Show top 20
    if result['confidence'] >= 20:  # Only show decent confidence
        count += 1
        print(f"#{count}. {result['predicted_crop'].upper()} - {result['confidence']:.2f}% Confidence {result['match']}")
        print("-" * 80)
        inp = result['input']
        print(f"   N (Nitrogen):     {inp[0]}")
        print(f"   P (Phosphorus):   {inp[1]}")
        print(f"   K (Potassium):    {inp[2]}")
        print(f"   Temperature:      {inp[3]}°C")
        print(f"   Humidity:         {inp[4]}%")
        print(f"   pH:               {inp[5]}")
        print(f"   Rainfall:         {inp[6]} mm")
        print()
        
        if count >= 10:
            break

print("="*80)
print(f"✅ Found {count} high confidence inputs for demonstration!")
print("="*80)

# Save to file
with open('HIGH_CONFIDENCE_10_CROPS.txt', 'w') as f:
    f.write("="*80 + "\n")
    f.write("HIGH CONFIDENCE INPUTS FOR 10+ CROPS\n")
    f.write("="*80 + "\n\n")
    
    count = 0
    for result in high_confidence_results[:20]:
        if result['confidence'] >= 20:
            count += 1
            inp = result['input']
            f.write(f"\n{count}. {result['predicted_crop'].upper()} - {result['confidence']:.2f}% Confidence {result['match']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"N: {inp[0]}, P: {inp[1]}, K: {inp[2]}, Temp: {inp[3]}, ")
            f.write(f"Humidity: {inp[4]}, pH: {inp[5]}, Rainfall: {inp[6]}\n")
            f.write(f"\nCopy-paste format:\n")
            f.write(f"N={inp[0]}, P={inp[1]}, K={inp[2]}, Temperature={inp[3]}, ")
            f.write(f"Humidity={inp[4]}, pH={inp[5]}, Rainfall={inp[6]}\n")
            
            if count >= 10:
                break
    
    f.write("\n" + "="*80 + "\n")
    f.write("Use any of these inputs in your demo for high confidence predictions!\n")
    f.write("="*80 + "\n")

print("\n💾 Results saved to: HIGH_CONFIDENCE_10_CROPS.txt")
print()
