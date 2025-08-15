#!/usr/bin/env python3
"""
Test script to verify waveform features calculation.
"""

import numpy as np
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.signal_processing import compute_waveform_features

def test_waveform_features():
    """Test the waveform features function with sample data."""
    
    # Load sample data
    try:
        df = pd.read_csv('sample_data/toy_PPG_data.csv')
        print(f"Loaded sample data with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")
        
        # Use PLETH column as waveform signal
        signal = df['PLETH'].values
        fs = 100.0  # 100 Hz sampling rate (10ms intervals)
        
        print(f"Signal shape: {signal.shape}")
        print(f"Signal range: {np.min(signal):.2f} to {np.max(signal):.2f}")
        print(f"Signal mean: {np.mean(signal):.2f}")
        print(f"Signal std: {np.std(signal):.2f}")
        
        # Compute features
        print("\nComputing waveform features...")
        features = compute_waveform_features(signal, fs)
        
        print(f"\nFeatures computed successfully!")
        print(f"Feature keys: {list(features.keys())}")
        
        if "statistical" in features:
            print(f"\nStatistical features:")
            for key, value in features["statistical"].items():
                print(f"  {key}: {value:.6f}")
        
        if "timing" in features:
            print(f"\nTiming features:")
            for key, value in features["timing"].items():
                print(f"  {key}: {value:.6f}")
        
        if "signal_quality" in features:
            print(f"\nSignal quality features:")
            for key, value in features["signal_quality"].items():
                print(f"  {key}: {value:.6f}")
        
        return features
        
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    features = test_waveform_features()
    if features:
        print("\n✅ Waveform features test passed!")
    else:
        print("\n❌ Waveform features test failed!")
