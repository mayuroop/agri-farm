"""
Brute Force Script to Find High Confidence Inputs for ALL Crops
This script systematically searches for optimal input combinations that give
high confidence predictions for every crop in the model.
"""

import numpy as np
import joblib
import pandas as pd
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("BRUTE FORCE SEARCH FOR HIGH CONFIDENCE INPUTS - ALL CROPS")
print("="*80)
print()

# Load the model
model_path = 'models/RandomForest.pkl'
print(f"Loading model from: {model_path}")
model = joblib.load(model_path)
print(f"Model loaded successfully!")
print()

# Get all crop classes
all_crops = sorted(model.classes_)
print(f"Total crops in model: {len(all_crops)}")
print(f"Crops: {', '.join(all_crops[:10])}{'...' if len(all_crops) > 10 else ''}")
print()

# Define search ranges for each parameter
# These are based on typical agricultural ranges
param_ranges = {
    'N': [20, 40, 60, 80, 100, 120, 150, 200],
    'P': [10, 20, 30, 40, 50, 60, 80, 100, 125],
    'K': [10, 20, 30, 40, 50, 60, 80, 100, 150, 200],
    'temperature': [15, 18, 20, 22, 25, 27, 30, 33, 35],
    'humidity': [20, 40, 50, 60, 70, 80, 85, 90, 95],
    'ph': [5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0],
    'rainfall': [25, 50, 75, 100, 200, 400, 600, 800, 1000, 1200, 1500, 1800, 2000]
}

print("Search ranges:")
for param, values in param_ranges.items():
    print(f"  {param:12s}: {len(values)} values from {min(values)} to {max(values)}")
print()

# Calculate total combinations
total_combinations = 1
for values in param_ranges.values():
    total_combinations *= len(values)
print(f"Total possible combinations: {total_combinations:,}")
print()

# Function to test a specific crop with targeted search
def find_best_for_crop(crop_name, model, param_ranges, max_samples=5000):
    """
    Find the best input combination for a specific crop using random sampling
    """
    best_confidence = 0
    best_input = None
    best_prediction = None
    
    # Random sampling from the parameter space
    np.random.seed(42)  # For reproducibility
    
    samples_tested = 0
    
    # Generate random samples
    for _ in range(max_samples):
        # Generate random input
        input_values = [
            np.random.choice(param_ranges['N']),
            np.random.choice(param_ranges['P']),
            np.random.choice(param_ranges['K']),
            np.random.choice(param_ranges['temperature']),
            np.random.choice(param_ranges['humidity']),
            np.random.choice(param_ranges['ph']),
            np.random.choice(param_ranges['rainfall'])
        ]
        
        X = np.array([input_values])
        
        try:
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            
            # Find the confidence for the target crop
            if crop_name in model.classes_:
                crop_index = list(model.classes_).index(crop_name)
                crop_confidence = probabilities[crop_index] * 100
                
                # If this prediction is for our target crop and has good confidence
                if prediction == crop_name and crop_confidence > best_confidence:
                    best_confidence = crop_confidence
                    best_input = input_values
                    best_prediction = prediction
            
            samples_tested += 1
            
        except Exception as e:
            continue
    
    return {
        'crop': crop_name,
        'predicted': best_prediction if best_prediction else 'Not Found',
        'confidence': best_confidence,
        'input': best_input,
        'samples_tested': samples_tested,
        'match': best_prediction == crop_name
    }

# Search for each crop
print("Starting brute force search for all crops...")
print("This may take a few minutes...\n")

all_results = []
found_count = 0

for i, crop_name in enumerate(all_crops, 1):
    print(f"[{i}/{len(all_crops)}] Searching for {crop_name:15s}... ", end='', flush=True)
    
    result = find_best_for_crop(crop_name, model, param_ranges, max_samples=5000)
    all_results.append(result)
    
    if result['match'] and result['confidence'] > 0:
        found_count += 1
        print(f"Found! {result['confidence']:.2f}% confidence")
    else:
        print(f"No direct match found (searched {result['samples_tested']} combinations)")

print()
print("="*80)
print(f"Search complete! Found high confidence inputs for {found_count}/{len(all_crops)} crops")
print("="*80)
print()

# Sort by confidence (descending)
all_results.sort(key=lambda x: x['confidence'], reverse=True)

# Display top results
print("\nTOP 20 HIGH CONFIDENCE RESULTS:")
print("-"*80)
for i, result in enumerate(all_results[:20], 1):
    if result['confidence'] > 0:
        status = "MATCH" if result['match'] else "DIFF"
        print(f"{i:2d}. {result['crop']:15s} -> {result['predicted']:15s} "
              f"{result['confidence']:6.2f}% [{status}]")

# Save results to CSV
csv_filename = 'all_crops_high_confidence.csv'
df_data = []
for result in all_results:
    if result['input']:
        row = {
            'crop': result['crop'],
            'predicted': result['predicted'],
            'confidence': result['confidence'],
            'match': result['match'],
            'N': result['input'][0],
            'P': result['input'][1],
            'K': result['input'][2],
            'temperature': result['input'][3],
            'humidity': result['input'][4],
            'ph': result['input'][5],
            'rainfall': result['input'][6]
        }
        df_data.append(row)

df = pd.DataFrame(df_data)
df = df.sort_values('confidence', ascending=False)
df.to_csv(csv_filename, index=False)
print(f"\n✓ CSV saved: {csv_filename}")

# Save to JSON
json_filename = 'all_crops_high_confidence.json'
json_data = {
    'generated_at': datetime.now().isoformat(),
    'model_path': model_path,
    'total_crops': len(all_crops),
    'crops_found': found_count,
    'results': []
}

for result in all_results:
    if result['input']:
        json_data['results'].append({
            'crop': result['crop'],
            'predicted': result['predicted'],
            'confidence': round(result['confidence'], 2),
            'match': result['match'],
            'input': {
                'N': result['input'][0],
                'P': result['input'][1],
                'K': result['input'][2],
                'temperature': result['input'][3],
                'humidity': result['input'][4],
                'ph': result['input'][5],
                'rainfall': result['input'][6]
            }
        })

with open(json_filename, 'w') as f:
    json.dump(json_data, f, indent=2)
print(f"✓ JSON saved: {json_filename}")

# Create detailed markdown report
md_filename = 'ALL_CROPS_HIGH_CONFIDENCE.md'
with open(md_filename, 'w', encoding='utf-8') as f:
    f.write("# Complete High Confidence Crop Inputs - All Crops\n\n")
    f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Total Crops**: {len(all_crops)}\n")
    f.write(f"**High Confidence Found**: {found_count}\n")
    f.write(f"**Model Accuracy**: 94.74%\n\n")
    f.write("---\n\n")
    
    # Summary table
    f.write("## Quick Reference Table\n\n")
    f.write("| # | Crop | Confidence | N | P | K | Temp | Humidity | pH | Rainfall | Status |\n")
    f.write("|---|------|-----------|---|---|---|------|----------|----|---------:|--------|\n")
    
    for i, result in enumerate(all_results[:30], 1):
        if result['input'] and result['confidence'] > 0:
            inp = result['input']
            status = "✅" if result['match'] else "⚠️"
            f.write(f"| {i} | {result['crop']} | {result['confidence']:.2f}% | "
                   f"{inp[0]} | {inp[1]} | {inp[2]} | {inp[3]} | {inp[4]} | "
                   f"{inp[5]} | {inp[6]} | {status} |\n")
    
    f.write("\n---\n\n")
    
    # Detailed entries
    f.write("## Detailed Input Data\n\n")
    
    for i, result in enumerate(all_results, 1):
        if result['input'] and result['confidence'] > 0:
            f.write(f"### {i}. {result['crop'].upper()}\n\n")
            f.write(f"**Confidence**: {result['confidence']:.2f}%\n")
            status_text = 'Correct Match' if result['match'] else f"Predicted as {result['predicted']}"
            status_emoji = '✅' if result['match'] else '⚠️'
            f.write(f"**Status**: {status_emoji} {status_text}\n\n")
            
            inp = result['input']
            f.write("```\n")
            f.write(f"N (Nitrogen):     {inp[0]}\n")
            f.write(f"P (Phosphorus):   {inp[1]}\n")
            f.write(f"K (Potassium):    {inp[2]}\n")
            f.write(f"Temperature:      {inp[3]}°C\n")
            f.write(f"Humidity:         {inp[4]}%\n")
            f.write(f"pH:               {inp[5]}\n")
            f.write(f"Rainfall:         {inp[6]} mm\n")
            f.write("```\n\n")
            f.write(f"**Copy-paste**: N={inp[0]}, P={inp[1]}, K={inp[2]}, "
                   f"Temp={inp[3]}, Humidity={inp[4]}, pH={inp[5]}, Rainfall={inp[6]}\n\n")
            f.write("---\n\n")

print(f"✓ Markdown saved: {md_filename}")

# Create a simple text file for easy reference
txt_filename = 'CROP_INPUTS_REFERENCE.txt'
with open(txt_filename, 'w') as f:
    f.write("="*80 + "\n")
    f.write("HIGH CONFIDENCE INPUTS - ALL CROPS REFERENCE\n")
    f.write("="*80 + "\n\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total crops: {len(all_crops)}\n")
    f.write(f"High confidence found: {found_count}\n\n")
    f.write("="*80 + "\n\n")
    
    for i, result in enumerate(all_results, 1):
        if result['input'] and result['confidence'] > 0:
            inp = result['input']
            status = "MATCH" if result['match'] else f"-> {result['predicted']}"
            f.write(f"{i}. {result['crop'].upper()} - {result['confidence']:.2f}% [{status}]\n")
            f.write("-"*80 + "\n")
            f.write(f"N={inp[0]}, P={inp[1]}, K={inp[2]}, Temp={inp[3]}, "
                   f"Humidity={inp[4]}, pH={inp[5]}, Rainfall={inp[6]}\n\n")

print(f"✓ Text file saved: {txt_filename}")

print()
print("="*80)
print("BRUTE FORCE SEARCH COMPLETE!")
print("="*80)
print()
print("Files generated:")
print(f"  1. {csv_filename} - CSV format for data analysis")
print(f"  2. {json_filename} - JSON format for API/web integration")
print(f"  3. {md_filename} - Detailed markdown documentation")
print(f"  4. {txt_filename} - Simple text reference")
print()
print(f"Summary: Found optimal inputs for {found_count} out of {len(all_crops)} crops")
print("="*80)
