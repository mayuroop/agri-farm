import pandas as pd
import numpy as np
import pickle

df = pd.read_csv('models/Crop_recommendation.csv')
m = pickle.load(open('models/model.pkl', 'rb'))

crops = df['label'].unique()
print(f'Testing all {len(crops)} crops for prediction and true confidence score:')
print('-'*100)

crop_dict = {
    1: 'Rice', 2: 'Maize', 3: 'Jute', 4: 'Cotton', 5: 'Coconut',
    6: 'Papaya', 7: 'Orange', 8: 'Apple', 9: 'Muskmelon',
    10: 'Watermelon', 11: 'Grapes', 12: 'Mango', 13: 'Banana',
    14: 'Pomegranate', 15: 'Lentil', 16: 'Blackgram', 17: 'Mungbean',
    18: 'Mothbeans', 19: 'Pigeonpeas', 20: 'Kidneybeans',
    21: 'Chickpea', 22: 'Coffee'
}

for crop in crops:
    # Get mean values for this crop as a typical profile
    crop_data = df[df['label'] == crop].select_dtypes(include=[np.number]).mean()
    x = np.array([crop_data.values])
    
    label_num = m.predict(x)[0]
    p = m.predict_proba(x)[0]
    conf = np.max(p) * 100
    
    pred_crop = crop_dict.get(label_num, 'Unknown')
    
    actual = crop.capitalize()
    print(f'Actual: {actual:<12} | Predicted: {pred_crop:<12} | Confidence: {conf:5.1f}% | '
          f'Profile: N={crop_data["N"]:.0f}, P={crop_data["P"]:.0f}, K={crop_data["K"]:.0f}, '
          f'Temp={crop_data["temperature"]:.1f}, Hum={crop_data["humidity"]:.1f}, '
          f'pH={crop_data["ph"]:.1f}, Rain={crop_data["rainfall"]:.0f}')

print('-'*100)
