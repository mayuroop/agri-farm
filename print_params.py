import pandas as pd
import numpy as np

df = pd.read_csv('models/Crop_recommendation.csv')
crops = df['label'].unique()

print('| Crop | Nitrogen (N) | Phosphorus (P) | Potassium (K) | Temp (°C) | Humidity (%) | pH | Rainfall (mm) |')
print('| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |')

for crop in sorted(crops):
    crop_data = df[df['label'] == crop].select_dtypes(include=[np.number]).mean()
    print(f'| **{crop.capitalize()}** | {crop_data["N"]:.1f} | {crop_data["P"]:.1f} | {crop_data["K"]:.1f} | {crop_data["temperature"]:.1f} | {crop_data["humidity"]:.1f} | {crop_data["ph"]:.1f} | {crop_data["rainfall"]:.1f} |')
