"""
House Price Data Preprocessing and Feature Engineering.
Prepares Bengaluru house data for price prediction modeling.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.parent
DATASET_DIR = PROJECT_DIR / "datasets"
PROCESSED_DIR = DATASET_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_house_data():
    """Load Bengaluru house price dataset."""
    df = pd.read_csv(DATASET_DIR / "Bengaluru_House_Data.csv")
    logger.info(f"Loaded house data: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")
    logger.info(f"Missing values:\n{df.isnull().sum()}")
    return df


def preprocess_house_data(df):
    """Clean and preprocess house dataset."""
    df = df.copy()
    
    # Remove rows with missing price or total_sqft
    df = df.dropna(subset=['price', 'total_sqft'])
    logger.info(f"After removing null prices: {df.shape}")
    
    # Clean total_sqft - convert ranges and non-numeric values
    df['total_sqft'] = df['total_sqft'].astype(str).str.split('-').str[0]
    df['total_sqft'] = pd.to_numeric(df['total_sqft'], errors='coerce')
    df = df.dropna(subset=['total_sqft'])
    
    # Remove outliers in price and sqft
    df = df[df['total_sqft'] > 100]  # Remove very small properties
    df = df[df['price'] > 10]  # Remove very cheap properties
    
    # Clean size column (e.g., "2 BHK" -> 2)
    df['bhk'] = df['size'].str.extract(r'(\d+)').astype(float)
    df = df[df['bhk'].notna()]
    
    # Feature engineering
    df['price_per_sqft'] = (df['price'] * 100000) / df['total_sqft']
    df['bath'] = pd.to_numeric(df['bath'], errors='coerce').fillna(df['bath'].median())
    df['balcony'] = pd.to_numeric(df['balcony'], errors='coerce').fillna(0)
    
    # Remove extreme outliers (using IQR method)
    Q1 = df['price_per_sqft'].quantile(0.25)
    Q3 = df['price_per_sqft'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[(df['price_per_sqft'] >= Q1 - 1.5*IQR) & (df['price_per_sqft'] <= Q3 + 1.5*IQR)]
    
    logger.info(f"After preprocessing: {df.shape}")
    logger.info(f"Price range: {df['price'].min()} - {df['price'].max()}")
    logger.info(f"Price per sqft range: {df['price_per_sqft'].min():.2f} - {df['price_per_sqft'].max():.2f}")
    
    return df


def encode_categorical_features(df):
    """Encode categorical features."""
    df = df.copy()
    
    # Encode area_type
    le_area = LabelEncoder()
    df['area_type_encoded'] = le_area.fit_transform(df['area_type'].fillna('Unknown'))
    
    # Encode availability
    le_avail = LabelEncoder()
    df['availability_encoded'] = le_avail.fit_transform(df['availability'].fillna('Unknown'))
    
    # Encode top locations (keep others as "Other")
    top_locations = df['location'].value_counts().head(10).index
    df['location_encoded'] = df['location'].apply(lambda x: x if x in top_locations else 'Other')
    le_loc = LabelEncoder()
    df['location_encoded'] = le_loc.fit_transform(df['location_encoded'])
    
    # Encode society (binary: has society or not)
    df['has_society'] = (~df['society'].isnull()).astype(int)
    
    return df


def create_features_for_ml(df):
    """Select and create final features for ML model."""
    df = df.copy()
    
    feature_cols = [
        'total_sqft',
        'bhk',
        'bath',
        'balcony',
        'price_per_sqft',
        'area_type_encoded',
        'availability_encoded',
        'location_encoded',
        'has_society'
    ]
    
    X = df[feature_cols].copy()
    y = df['price'].copy()
    
    # Handle any remaining NaNs
    X = X.fillna(X.mean())
    
    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Features: {feature_cols}")
    
    return X, y, feature_cols


def main():
    """Main preprocessing pipeline."""
    df = load_house_data()
    df = preprocess_house_data(df)
    df = encode_categorical_features(df)
    X, y, feature_cols = create_features_for_ml(df)
    
    # Save processed data
    X.to_csv(PROCESSED_DIR / "house_features.csv", index=False)
    y.to_csv(PROCESSED_DIR / "house_prices.csv", index=False)
    pd.DataFrame({'feature': feature_cols}).to_csv(PROCESSED_DIR / "house_feature_columns.csv", index=False)
    
    logger.info(f"Saved to {PROCESSED_DIR}")
    logger.info(f"Feature count: {len(feature_cols)}")
    
    return X, y, feature_cols


if __name__ == "__main__":
    main()
