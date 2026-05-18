"""
House Price Prediction Service.
Provides inference for residential property price estimation.
Used as collateral valuation and financial health indicator.
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class HousePriceService:
    """Service for house price prediction."""
    
    def __init__(self, model_dir: Path | None = None):
        """Initialize house price prediction service.
        
        Parameters
        ----------
        model_dir : Path, optional
            Directory containing model artifacts. If None, uses default backend/models.
        """
        if model_dir is None:
            current_dir = Path(__file__).resolve().parent.parent.parent  # backend
            model_dir = current_dir / "models"
        
        self.model_dir = model_dir
        self.models = {}
        self.features = None
        self.scalers = {}
        self.is_loaded = False
        
        self._load_artifacts()
    
    def _load_artifacts(self) -> None:
        """Load all house price models and feature information."""
        try:
            # Load feature columns
            feature_file = self.model_dir / "house_price_features.pkl"
            if feature_file.exists():
                self.features = joblib.load(feature_file)
                logger.info(f"Loaded features: {len(self.features)} features")
            
            # Load models
            model_names = ['xgboost', 'random_forest', 'linear_regression']
            for model_name in model_names:
                model_file = self.model_dir / f"house_price_{model_name}.joblib"
                scaler_file = self.model_dir / f"house_price_{model_name}_scaler.joblib"
                
                if model_file.exists():
                    self.models[model_name] = joblib.load(model_file)
                    logger.info(f"Loaded model: {model_name}")
                    
                    if scaler_file.exists():
                        self.scalers[model_name] = joblib.load(scaler_file)
            
            self.is_loaded = len(self.models) > 0 and self.features is not None
            
            if not self.is_loaded:
                logger.warning("House price models not fully loaded")
        
        except Exception as e:
            logger.error(f"Error loading house price artifacts: {e}")
            self.is_loaded = False
    
    def prepare_features(self, input_data: Dict) -> Tuple[np.ndarray, bool]:
        """Prepare and validate input features.
        
        Parameters
        ----------
        input_data : Dict
            Input features dictionary with keys:
            - total_sqft: Total square feet
            - bhk: Number of bedrooms
            - bath: Number of bathrooms
            - balcony: Number of balconies
            - price_per_sqft: Price per square foot (optional, computed if not provided)
            - area_type_encoded: Encoded area type
            - availability_encoded: Encoded availability
            - location_encoded: Encoded location
            - has_society: Binary indicator for society
        
        Returns
        -------
        Tuple[np.ndarray, bool]
            Feature array and validation flag
        """
        try:
            # Extract features in order
            feature_values = []
            for feature in self.features:
                value = input_data.get(feature)
                
                if value is None:
                    logger.warning(f"Missing feature: {feature}")
                    return None, False
                
                feature_values.append(float(value))
            
            return np.array(feature_values).reshape(1, -1), True
        
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None, False
    
    def predict_price(self, input_data: Dict, model_name: str = 'xgboost') -> Dict:
        """Predict house price.
        
        Parameters
        ----------
        input_data : Dict
            Input features
        model_name : str, optional
            Model to use ('xgboost', 'random_forest', 'linear_regression')
        
        Returns
        -------
        Dict
            Prediction result with:
            - predicted_price: Estimated price in millions
            - confidence: Model confidence (0-1)
            - uncertainty: Estimated uncertainty in price
            - model_used: Name of model used
            - status: 'success' or 'error'
        """
        if not self.is_loaded:
            return {
                'status': 'error',
                'message': 'House price models not loaded'
            }
        
        if model_name not in self.models:
            return {
                'status': 'error',
                'message': f'Model {model_name} not available'
            }
        
        try:
            # Prepare features
            X_input, is_valid = self.prepare_features(input_data)
            if not is_valid or X_input is None:
                return {
                    'status': 'error',
                    'message': 'Invalid input features'
                }
            
            # Scale if scaler exists
            model = self.models[model_name]
            if model_name in self.scalers:
                X_input = self.scalers[model_name].transform(X_input)
            
            # Predict
            prediction = model.predict(X_input)[0]
            
            # Confidence estimation
            if hasattr(model, 'predict_proba'):
                # For probabilistic models
                confidence = np.max(model.predict_proba(X_input)) if hasattr(model, 'predict_proba') else 0.8
            else:
                # For tree-based models
                confidence = min(0.95, abs(prediction) / max(abs(prediction), 1e6))
            
            # Uncertainty estimation (simplified)
            uncertainty = prediction * 0.15  # 15% uncertainty band
            
            return {
                'status': 'success',
                'predicted_price': round(float(prediction), 2),
                'predicted_price_formatted': f"₹{prediction:.2f} Cr",
                'confidence': round(float(confidence), 2),
                'uncertainty': round(float(uncertainty), 2),
                'uncertainty_range': {
                    'lower': round(float(prediction - uncertainty), 2),
                    'upper': round(float(prediction + uncertainty), 2)
                },
                'model_used': model_name,
                'input_features': input_data
            }
        
        except Exception as e:
            logger.error(f"Error predicting price: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def predict_ensemble(self, input_data: Dict) -> Dict:
        """Predict using ensemble of all available models.
        
        Returns
        -------
        Dict
            Ensemble prediction with:
            - ensemble_price: Average prediction
            - individual_predictions: Predictions from each model
            - consensus: Confidence in ensemble
        """
        try:
            X_input, is_valid = self.prepare_features(input_data)
            if not is_valid or X_input is None:
                return {'status': 'error', 'message': 'Invalid input features'}
            
            predictions = {}
            prices = []
            
            for model_name in self.models:
                model = self.models[model_name]
                
                X = X_input.copy()
                if model_name in self.scalers:
                    X = self.scalers[model_name].transform(X)
                
                pred = model.predict(X)[0]
                predictions[model_name] = round(float(pred), 2)
                prices.append(float(pred))
            
            ensemble_price = np.mean(prices)
            std_price = np.std(prices)
            consensus = 1 - min(std_price / ensemble_price, 0.5) if ensemble_price > 0 else 0
            
            return {
                'status': 'success',
                'ensemble_price': round(ensemble_price, 2),
                'ensemble_price_formatted': f"₹{ensemble_price:.2f} Cr",
                'individual_predictions': predictions,
                'consensus': round(float(consensus), 2),
                'std_deviation': round(float(std_price), 2),
                'uncertainty_range': {
                    'lower': round(ensemble_price - std_price, 2),
                    'upper': round(ensemble_price + std_price, 2)
                }
            }
        
        except Exception as e:
            logger.error(f"Error in ensemble prediction: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def health_check(self) -> Dict:
        """Check service health and model availability."""
        return {
            'status': 'healthy' if self.is_loaded else 'unhealthy',
            'models_loaded': list(self.models.keys()),
            'features_loaded': self.features is not None,
            'num_features': len(self.features) if self.features else 0,
            'model_dir': str(self.model_dir)
        }
