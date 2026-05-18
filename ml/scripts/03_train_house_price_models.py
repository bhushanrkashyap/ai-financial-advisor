"""
House Price Prediction Model Training.
Trains XGBoost, Random Forest, and Linear Regression models.
Saves best model artifacts for backend integration.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import joblib
import logging
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.parent
PROCESSED_DIR = PROJECT_DIR / "datasets" / "processed"
MODEL_DIR = PROJECT_DIR / "backend" / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def load_processed_data():
    """Load preprocessed house data."""
    X = pd.read_csv(PROCESSED_DIR / "house_features.csv")
    y = pd.read_csv(PROCESSED_DIR / "house_prices.csv").squeeze()
    
    logger.info(f"Loaded data: X={X.shape}, y={y.shape}")
    logger.info(f"Price stats - Mean: {y.mean():.2f}, Std: {y.std():.2f}, Min: {y.min():.2f}, Max: {y.max():.2f}")
    
    return X, y


def prepare_train_test_data(X, y):
    """Split data into train/validation/test sets."""
    # 70% train, 15% val, 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.176, random_state=42  # ~15% of total
    )
    
    logger.info(f"Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
    
    return X_train, X_val, X_test, y_train, y_val, y_test


def train_linear_regression(X_train, y_train, X_val, y_val):
    """Train baseline linear regression model."""
    logger.info("Training Linear Regression...")
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    model = Ridge(alpha=1.0)
    model.fit(X_train_scaled, y_train)
    
    train_pred = model.predict(X_train_scaled)
    val_pred = model.predict(X_val_scaled)
    
    train_r2 = r2_score(y_train, train_pred)
    val_r2 = r2_score(y_val, val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
    val_mae = mean_absolute_error(y_val, val_pred)
    
    logger.info(f"Linear Regression - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
    logger.info(f"Val RMSE: {val_rmse:.2f}, Val MAE: {val_mae:.2f}")
    
    return {'model': model, 'scaler': scaler, 'train_r2': train_r2, 'val_r2': val_r2, 
            'val_rmse': val_rmse, 'val_mae': val_mae}


def train_random_forest(X_train, y_train, X_val, y_val):
    """Train Random Forest model."""
    logger.info("Training Random Forest...")
    
    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    model.fit(X_train, y_train)
    
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    
    train_r2 = r2_score(y_train, train_pred)
    val_r2 = r2_score(y_val, val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
    val_mae = mean_absolute_error(y_val, val_pred)
    
    logger.info(f"Random Forest - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
    logger.info(f"Val RMSE: {val_rmse:.2f}, Val MAE: {val_mae:.2f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    logger.info(f"Top features:\n{feature_importance.head(10)}")
    
    return {'model': model, 'train_r2': train_r2, 'val_r2': val_r2,
            'val_rmse': val_rmse, 'val_mae': val_mae, 'feature_importance': feature_importance}


def train_xgboost(X_train, y_train, X_val, y_val):
    """Train XGBoost model with hyperparameter tuning."""
    logger.info("Training XGBoost...")
    
    # Scale data for XGBoost
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    
    # Initial model
    model = XGBRegressor(
        objective='reg:squarederror',
        n_estimators=500,
        learning_rate=0.05,
        max_depth=7,
        min_child_weight=1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=1
    )
    
    # Train with early stopping
    model.fit(
        X_train_scaled, y_train,
        eval_set=[(X_val_scaled, y_val)],
        verbose=False
    )
    
    train_pred = model.predict(X_train_scaled)
    val_pred = model.predict(X_val_scaled)
    
    train_r2 = r2_score(y_train, train_pred)
    val_r2 = r2_score(y_val, val_pred)
    val_rmse = np.sqrt(mean_squared_error(y_val, val_pred))
    val_mae = mean_absolute_error(y_val, val_pred)
    
    logger.info(f"XGBoost - Train R²: {train_r2:.4f}, Val R²: {val_r2:.4f}")
    logger.info(f"Val RMSE: {val_rmse:.2f}, Val MAE: {val_mae:.2f}")
    # logger.info(f"Best iteration: {model.best_iteration}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    logger.info(f"Top features:\n{feature_importance.head(10)}")
    
    return {'model': model, 'scaler': scaler, 'train_r2': train_r2, 'val_r2': val_r2,
            'val_rmse': val_rmse, 'val_mae': val_mae, 'feature_importance': feature_importance}


def evaluate_on_test(model_info, X_test, y_test, model_name):
    """Evaluate model on test set."""
    model = model_info['model']
    
    if 'scaler' in model_info:
        X_test_scaled = model_info['scaler'].transform(X_test)
        test_pred = model.predict(X_test_scaled)
    else:
        test_pred = model.predict(X_test)
    
    test_r2 = r2_score(y_test, test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    test_mae = mean_absolute_error(y_test, test_pred)
    
    logger.info(f"{model_name} Test Set - R²: {test_r2:.4f}, RMSE: {test_rmse:.2f}, MAE: {test_mae:.2f}")
    
    return {'test_r2': test_r2, 'test_rmse': test_rmse, 'test_mae': test_mae}


def save_model_artifacts(model_info, X_train, model_name, scaler_name=None):
    """Save trained model and feature information."""
    model_path = MODEL_DIR / f"house_price_{model_name}.joblib"
    feature_path = MODEL_DIR / "house_price_features.pkl"
    
    joblib.dump(model_info['model'], model_path)
    joblib.dump(list(X_train.columns), feature_path)
    
    if 'scaler' in model_info:
        scaler_path = MODEL_DIR / f"house_price_{model_name}_scaler.joblib"
        joblib.dump(model_info['scaler'], scaler_path)
        logger.info(f"Saved scaler to {scaler_path}")
    
    logger.info(f"Saved model to {model_path}")
    logger.info(f"Saved features to {feature_path}")


def main():
    """Main training pipeline."""
    X, y = load_processed_data()
    X_train, X_val, X_test, y_train, y_val, y_test = prepare_train_test_data(X, y)
    
    # Train models
    lr_model = train_linear_regression(X_train, y_train, X_val, y_val)
    rf_model = train_random_forest(X_train, y_train, X_val, y_val)
    xgb_model = train_xgboost(X_train, y_train, X_val, y_val)
    
    # Evaluate on test set
    logger.info("\n=== TEST SET EVALUATION ===")
    lr_test = evaluate_on_test(lr_model, X_test, y_test, "Linear Regression")
    rf_test = evaluate_on_test(rf_model, X_test, y_test, "Random Forest")
    xgb_test = evaluate_on_test(xgb_model, X_test, y_test, "XGBoost")
    
    # Choose best model (based on validation R²)
    models = {
        'linear_regression': {**lr_model, **lr_test},
        'random_forest': {**rf_model, **rf_test},
        'xgboost': {**xgb_model, **xgb_test}
    }
    
    best_model_name = max(models, key=lambda x: models[x]['val_r2'])
    logger.info(f"\n=== BEST MODEL: {best_model_name} ===")
    logger.info(f"Validation R²: {models[best_model_name]['val_r2']:.4f}")
    logger.info(f"Test R²: {models[best_model_name]['test_r2']:.4f}")
    
    # Save all models
    for model_name, model_info in models.items():
        save_model_artifacts(model_info, X_train, model_name)
    
    # Save model comparison
    comparison_df = pd.DataFrame({
        'Model': list(models.keys()),
        'Train R²': [models[m]['train_r2'] for m in models],
        'Val R²': [models[m]['val_r2'] for m in models],
        'Test R²': [models[m]['test_r2'] for m in models],
        'Val RMSE': [models[m]['val_rmse'] for m in models],
        'Test RMSE': [models[m]['test_rmse'] for m in models],
    })
    comparison_df.to_csv(MODEL_DIR / "house_price_model_comparison.csv", index=False)
    logger.info(f"\nModel comparison:\n{comparison_df.to_string()}")
    
    return best_model_name, models


if __name__ == "__main__":
    main()
