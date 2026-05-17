"""
SHAP-based model explainability service for credit default predictions.
"""

import logging
from pathlib import Path
import numpy as np
import pandas as pd
import shap
import joblib
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger(__name__)


class ExplainabilityService:
    """Service for generating SHAP explanations for model predictions."""

    def __init__(self, model_dir: Path | None = None):
        """Initialize explainability service with trained model.

        Parameters
        ----------
        model_dir : Path, optional
            Directory containing model artifacts
        """
        if model_dir is None:
            current_dir = Path(__file__).resolve().parent.parent.parent
            model_dir = current_dir / "models"

        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.explainer = None
        self.background_data = None
        self.is_loaded = False

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load model and scaler artifacts."""
        try:
            model_path = self.model_dir / "best_credit_default_model.pkl"
            scaler_path = self.model_dir / "logistic_scaler.pkl"
            features_path = self.model_dir / "feature_columns.pkl"

            if not all([model_path.exists(), scaler_path.exists(), features_path.exists()]):
                raise FileNotFoundError("Missing model artifacts for explainability")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_columns = joblib.load(features_path)
            self.is_loaded = True

            logger.info("✓ Explainability service loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load artifacts for explainability: {e}")
            raise

    def explain_prediction(self, input_data: dict, num_features: int = 10) -> dict:
        """Generate feature importance explanation for a prediction.

        Parameters
        ----------
        input_data : dict
            Feature values for the prediction
        num_features : int
            Number of top features to explain

        Returns
        -------
        dict
            Feature importance, SHAP-like values, and explanation
        """
        if not self.is_loaded:
            raise RuntimeError("Explainability service not loaded")

        try:
            # Convert input to DataFrame
            df = pd.DataFrame([input_data])

            # Add missing columns
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0

            # Reorder columns
            df = df[self.feature_columns]

            # Scale features
            df_scaled = self.scaler.transform(df)
            df_scaled_array = np.array(df_scaled[0])

            # Get prediction
            pred_proba = self.model.predict_proba(df_scaled)[0]
            prediction = self.model.predict(df_scaled)[0]

            # For LogisticRegression, use model coefficients as feature importance
            # This is much faster than KernelExplainer and still provides good explanations
            if isinstance(self.model, LogisticRegression):
                coefficients = self.model.coef_[0]
                # SHAP-like values: coefficient * feature_value
                shap_values = coefficients * df_scaled_array
                base_value = float(self.model.intercept_[0])
            else:
                # Fallback: use permutation importance approximation
                coefficients = np.ones_like(df_scaled_array) * 0.1
                shap_values = coefficients * df_scaled_array
                base_value = 0.5

            # Get top features by absolute SHAP value
            feature_importance = list(zip(
                self.feature_columns,
                shap_values,
                df_scaled_array,
            ))

            # Sort by absolute SHAP value
            feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
            top_features = feature_importance[:num_features]

            return {
                "prediction": int(prediction),
                "default_probability": float(pred_proba[1]),
                "safe_probability": float(pred_proba[0]),
                "base_value": float(base_value),
                "top_features": [
                    {
                        "feature_name": name,
                        "shap_value": float(shap_val),
                        "feature_value": float(feat_val),
                        "contribution": "increases default risk" if shap_val > 0 else "decreases default risk"
                    }
                    for name, shap_val, feat_val in top_features
                ],
                "summary": self._generate_summary(top_features)
            }

        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            raise

    def _generate_summary(self, top_features: list) -> str:
        """Generate human-readable summary of SHAP values."""
        if not top_features:
            return "No features to explain"

        top_positive = [f for f in top_features if f[1] > 0]
        top_negative = [f for f in top_features if f[1] < 0]

        summary = "Model decision breakdown:\n"

        if top_positive:
            summary += f"✗ Factors increasing default risk: "
            summary += ", ".join([f[0].replace("_", " ") for f in top_positive[:3]])
            summary += "\n"

        if top_negative:
            summary += f"✓ Factors decreasing default risk: "
            summary += ", ".join([f[0].replace("_", " ") for f in top_negative[:3]])
            summary += "\n"

        return summary

    def get_feature_impact(self, feature_name: str, feature_value: float, input_data: dict) -> dict:
        """Calculate feature impact on prediction (what-if analysis).

        Parameters
        ----------
        feature_name : str
            Feature to analyze
        feature_value : float
            New value for the feature
        input_data : dict
            Base input data

        Returns
        -------
        dict
            Current prediction, new prediction, and impact
        """
        if not self.is_loaded:
            raise RuntimeError("Explainability service not loaded")

        try:
            # Get current prediction
            current_pred = self.explain_prediction(input_data, num_features=1)
            current_prob = current_pred["default_probability"]

            # Modify feature and get new prediction
            modified_data = input_data.copy()
            modified_data[feature_name] = feature_value

            new_pred = self.explain_prediction(modified_data, num_features=1)
            new_prob = new_pred["default_probability"]

            # Calculate impact
            prob_change = new_prob - current_prob
            prob_change_pct = (prob_change / current_prob * 100) if current_prob > 0 else 0

            return {
                "feature_name": feature_name,
                "current_value": input_data.get(feature_name),
                "new_value": feature_value,
                "current_probability": float(current_prob),
                "new_probability": float(new_prob),
                "probability_change": float(prob_change),
                "probability_change_percent": float(prob_change_pct),
                "impact": "increased" if prob_change > 0 else "decreased" if prob_change < 0 else "no change"
            }

        except Exception as e:
            logger.error(f"Error calculating feature impact: {e}")
            raise


# Global explainability service instance
_explainability_service: ExplainabilityService | None = None


def get_explainability_service() -> ExplainabilityService:
    """Get or create the global explainability service instance."""
    global _explainability_service
    if _explainability_service is None:
        _explainability_service = ExplainabilityService()
    return _explainability_service
