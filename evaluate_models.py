"""
Model Evaluation Script for AgriFarm ML Models
This script evaluates the accuracy of:
1. RandomForest Crop Recommendation Model
2. Plant Disease Detection Model (PyTorch)
"""

import numpy as np
import pandas as pd
import pickle
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image

# ============================================================================
# 1. CROP RECOMMENDATION MODEL EVALUATION (RandomForest)
# ============================================================================

def evaluate_crop_recommendation_model():
    """Evaluate the RandomForest crop recommendation model"""
    print("="*80)
    print("EVALUATING CROP RECOMMENDATION MODEL (RandomForest)")
    print("="*80)
    
    try:
        # Load the model
        model_path = os.path.join('models', 'RandomForest.pkl')
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            return
        
        print(f"📂 Loading model from: {model_path}")
        
        try:
            model = joblib.load(model_path)
            print("✅ Model loaded successfully with joblib")
        except:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print("✅ Model loaded successfully with pickle")
        
        # Load the dataset
        data_path = os.path.join('Data', 'crop_recommendation.csv')
        
        if not os.path.exists(data_path):
            print(f"❌ Dataset not found at: {data_path}")
            return
        
        print(f"📂 Loading dataset from: {data_path}")
        df = pd.read_csv(data_path)
        print(f"✅ Dataset loaded: {len(df)} samples")
        print(f"   Features: N, P, K, temperature, humidity, ph, rainfall")
        print(f"   Classes: {df['label'].unique().tolist()}")
        print(f"   Number of classes: {df['label'].nunique()}")
        
        # Prepare data
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
        y = df['label'].values
        
        # Split data (use same split as during training if possible)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📊 Data split:")
        print(f"   Training samples: {len(X_train)}")
        print(f"   Testing samples: {len(X_test)}")
        
        # Make predictions
        print("\n🔮 Making predictions...")
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate accuracies
        train_accuracy = accuracy_score(y_train, y_pred_train)
        test_accuracy = accuracy_score(y_test, y_pred_test)
        
        print("\n" + "="*80)
        print("📈 CROP RECOMMENDATION MODEL RESULTS")
        print("="*80)
        print(f"🎯 Training Accuracy: {train_accuracy*100:.2f}%")
        print(f"🎯 Testing Accuracy:  {test_accuracy*100:.2f}%")
        print(f"📉 Overfitting Check: {abs(train_accuracy - test_accuracy)*100:.2f}% difference")
        
        if abs(train_accuracy - test_accuracy) < 0.05:
            print("✅ Model is well-balanced (low overfitting)")
        elif abs(train_accuracy - test_accuracy) < 0.10:
            print("⚠️  Model shows slight overfitting")
        else:
            print("❌ Model shows significant overfitting")
        
        # Classification report
        print("\n📊 DETAILED CLASSIFICATION REPORT:")
        print("-"*80)
        print(classification_report(y_test, y_pred_test, zero_division=0))
        
        # Per-class accuracy
        print("\n📊 PER-CLASS ACCURACY:")
        print("-"*80)
        for crop in sorted(df['label'].unique()):
            crop_indices = y_test == crop
            if crop_indices.sum() > 0:
                crop_accuracy = accuracy_score(
                    y_test[crop_indices], 
                    y_pred_test[crop_indices]
                )
                print(f"   {crop:15s}: {crop_accuracy*100:6.2f}%")
        
        # Save results to file
        with open('crop_model_evaluation_results.txt', 'w') as f:
            f.write("CROP RECOMMENDATION MODEL EVALUATION RESULTS\n")
            f.write("="*80 + "\n\n")
            f.write(f"Training Accuracy: {train_accuracy*100:.2f}%\n")
            f.write(f"Testing Accuracy: {test_accuracy*100:.2f}%\n\n")
            f.write("Classification Report:\n")
            f.write(classification_report(y_test, y_pred_test, zero_division=0))
        
        print("\n💾 Results saved to: crop_model_evaluation_results.txt")
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy,
            'model_type': 'RandomForest'
        }
        
    except Exception as e:
        print(f"❌ Error evaluating crop recommendation model: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# 2. PLANT DISEASE MODEL EVALUATION (PyTorch)
# ============================================================================

def evaluate_disease_model():
    """Evaluate the plant disease detection model"""
    print("\n" + "="*80)
    print("EVALUATING PLANT DISEASE DETECTION MODEL (PyTorch ResNet9)")
    print("="*80)
    
    try:
        model_path = os.path.join('models', 'plant_disease_model.pth')
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found at: {model_path}")
            return
        
        print(f"📂 Model found at: {model_path}")
        print(f"📦 Model size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
        
        # Try to load the model
        try:
            checkpoint = torch.load(model_path, map_location=torch.device('cpu'))
            print("✅ Model checkpoint loaded successfully")
            
            # Check what's in the checkpoint
            if isinstance(checkpoint, dict):
                print("\n📋 Checkpoint contents:")
                for key in checkpoint.keys():
                    print(f"   - {key}")
                
                # Try to get model info
                if 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                elif 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                else:
                    state_dict = checkpoint
                
                # Count parameters
                total_params = sum(p.numel() for p in state_dict.values() if isinstance(p, torch.Tensor))
                print(f"\n📊 Model Statistics:")
                print(f"   Total parameters: {total_params:,}")
                print(f"   Model architecture: ResNet9 (as per documentation)")
                
                # Check for training metrics in checkpoint
                if 'accuracy' in checkpoint:
                    print(f"\n🎯 Saved Training Accuracy: {checkpoint['accuracy']*100:.2f}%")
                if 'val_accuracy' in checkpoint:
                    print(f"🎯 Saved Validation Accuracy: {checkpoint['val_accuracy']*100:.2f}%")
                if 'test_accuracy' in checkpoint:
                    print(f"🎯 Saved Test Accuracy: {checkpoint['test_accuracy']*100:.2f}%")
                
                if 'classes' in checkpoint:
                    classes = checkpoint['classes']
                    print(f"\n📋 Number of disease classes: {len(classes)}")
                    print("   Classes:", classes[:5], "..." if len(classes) > 5 else "")
            
            print("\n⚠️  Note: To fully evaluate this model, you need:")
            print("   1. Test dataset with labeled disease images")
            print("   2. ResNet9 model architecture definition")
            print("   3. Same preprocessing pipeline used during training")
            print("\n💡 The model appears to be properly saved and can be loaded.")
            print("   According to documentation: 90%+ accuracy expected on test images")
            
            # Save info
            with open('disease_model_info.txt', 'w') as f:
                f.write("PLANT DISEASE DETECTION MODEL INFO\n")
                f.write("="*80 + "\n\n")
                f.write(f"Model Path: {model_path}\n")
                f.write(f"Model Size: {os.path.getsize(model_path) / (1024*1024):.2f} MB\n")
                f.write(f"Total Parameters: {total_params:,}\n")
                f.write(f"Architecture: ResNet9\n")
                f.write(f"Expected Accuracy: 90%+ (as per documentation)\n")
                if isinstance(checkpoint, dict):
                    f.write(f"\nCheckpoint keys: {list(checkpoint.keys())}\n")
            
            print("\n💾 Model info saved to: disease_model_info.txt")
            
            return {
                'model_path': model_path,
                'model_type': 'ResNet9',
                'total_params': total_params
            }
            
        except Exception as load_error:
            print(f"❌ Error loading model: {load_error}")
            return None
            
    except Exception as e:
        print(f"❌ Error evaluating disease model: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main evaluation function"""
    print("\n")
    print("*"*80)
    print(" "*20 + "AGRIFARM MODEL EVALUATION SUITE")
    print("*"*80)
    print()
    
    # Evaluate Crop Recommendation Model
    crop_results = evaluate_crop_recommendation_model()
    
    # Evaluate Disease Detection Model
    disease_results = evaluate_disease_model()
    
    # Summary
    print("\n" + "="*80)
    print("📊 EVALUATION SUMMARY")
    print("="*80)
    
    if crop_results:
        print(f"\n✅ Crop Recommendation Model (RandomForest):")
        print(f"   - Training Accuracy: {crop_results['train_accuracy']*100:.2f}%")
        print(f"   - Testing Accuracy: {crop_results['test_accuracy']*100:.2f}%")
    else:
        print("\n❌ Crop Recommendation Model: Evaluation failed")
    
    if disease_results:
        print(f"\n✅ Disease Detection Model (ResNet9):")
        print(f"   - Model loaded successfully")
        print(f"   - Parameters: {disease_results['total_params']:,}")
        print(f"   - Note: Full accuracy evaluation requires test dataset")
    else:
        print("\n❌ Disease Detection Model: Evaluation failed")
    
    print("\n" + "="*80)
    print("✨ Evaluation complete! Check the generated .txt files for details.")
    print("="*80)
    print()


if __name__ == "__main__":
    main()
