"""
Credit default prediction service.
"""

import logging
from pathlib import Path

import joblib
import httpx
import numpy as np
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)


def _prediction_trace_logging() -> bool:
    return bool(settings.debug or settings.prediction_verbose_logs)


class CreditDefaultPredictionService:
    """Service for credit default predictions using the trained model."""

    def __init__(self, model_dir: Path | None = None):
        """Initialize the prediction service.

        Parameters
        ----------
        model_dir : Path, optional
            Directory containing model artifacts. If None, uses default backend/models.
        """
        if model_dir is None:
            # Infer model directory from current location
            # prediction.py is at backend/app/services/prediction.py
            # So we need to go up 3 levels to get to backend, then into models
            current_dir = Path(__file__).resolve().parent.parent.parent  # backend
            model_dir = current_dir / "models"

        self.model_dir = model_dir
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.is_loaded = False

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load model, scaler, and feature columns from disk."""
        try:
            model_path = self.model_dir / "best_credit_default_model.pkl"
            scaler_path = self.model_dir / "logistic_scaler.pkl"
            features_path = self.model_dir / "feature_columns.pkl"

            if not all([model_path.exists(), scaler_path.exists(), features_path.exists()]):
                missing = [
                    p.name
                    for p in [model_path, scaler_path, features_path]
                    if not p.exists()
                ]
                raise FileNotFoundError(f"Missing model artifacts: {missing}")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_columns = joblib.load(features_path)
            self.is_loaded = True

            logger.info(
                f"✓ Loaded model from {model_path}",
            )
            logger.info(
                f"✓ Loaded {len(self.feature_columns)} features",
            )

        except Exception as e:
            logger.error(f"Failed to load model artifacts: {e}")
            raise

    def predict(self, input_data: dict) -> dict:
        """Make a prediction for a single loan application with comprehensive validation.

        Parameters
        ----------
        input_data : dict
            Dictionary with feature values (keys must match feature_columns)

        Returns
        -------
        dict
            Prediction results including probability and risk level
        """
        if not self.is_loaded:
            raise RuntimeError("Model artifacts not loaded")

        trace = _prediction_trace_logging()
        if trace:
            logger.debug("prediction request payload=%s", input_data)

        # ========== VALIDATION CHECKS ==========
        validation_result = self._validate_hard_rules(input_data)
        if validation_result:
            logger.warning("Hard rule rejection: %s", validation_result["recommendation"])
            return validation_result

        # Convert input to DataFrame
        df = pd.DataFrame([input_data])

        if trace:
            logger.debug("dataframe columns (raw)=%s", df.columns.tolist())

        # Add missing columns with zeros for features not provided
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0

        # Reorder to match training features
        df = df[self.feature_columns]

        if trace:
            logger.debug(
                "aligned row fico=%s dti=%s delinq=%s emp_length=%s",
                float(df["fico_avg"].iloc[0]),
                float(df["dti"].iloc[0]),
                int(df["delinq_2yrs"].iloc[0]),
                int(df["emp_length"].iloc[0]),
            )

        # Scale features
        df_scaled = self.scaler.transform(df)

        # Get prediction and probabilities
        pred = self.model.predict(df_scaled)[0]
        proba = self.model.predict_proba(df_scaled)[0]
        prob_safe, prob_default = self._binary_safe_default_probs(proba)

        if trace:
            logger.debug(
                "classes=%s pred=%s proba=%s prob_safe=%.4f prob_default=%.4f",
                getattr(self.model, "classes_", None),
                pred,
                proba,
                prob_safe,
                prob_default,
            )

        # Determine risk level based on default probability
        if prob_default < 0.3:
            risk_level = "LOW_RISK"
        elif prob_default < 0.6:
            risk_level = "MEDIUM_RISK"
        else:
            risk_level = "HIGH_RISK"

        # Determine confidence (distance from 0.5 threshold)
        confidence = abs(prob_default - 0.5) * 2  # Scale to 0-1
        confidence = min(1.0, max(0.0, confidence))

        if trace:
            logger.debug("risk=%s confidence=%.4f", risk_level, confidence)

        # Get recommendation from Java engine
        recommendation = self._get_java_recommendation(
            input_data, prob_default, risk_level
        )

        result = {
            "prediction": "DEFAULT_RISK" if pred == 1 else "SAFE",
            "default_probability": prob_default,
            "safe_probability": prob_safe,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "confidence_score": confidence,
        }

        logger.info(
            "credit prediction risk=%s p_default=%.4f prediction=%s",
            risk_level,
            prob_default,
            result["prediction"],
        )

        # Record in analytics
        try:
            from app.services.analytics import get_analytics_service
            
            analytics = get_analytics_service()
            
            # Extract key fields for analytics
            loan_amount = input_data.get("loan_amnt", 0)
            fico_score = int(input_data.get("fico_avg", 650))
            dti_ratio = float(input_data.get("dti", 0.3))
            interest_rate = float(input_data.get("int_rate", 0))
            
            # Calculate approval probability for analytics
            from app.services.financial_calculator import get_financial_calculator
            calculator = get_financial_calculator()
            approval_data = calculator.calculate_approval_probability_score(
                prob_default,
                dti_ratio,
                fico_score,
                int(input_data.get("emp_length", 0)),
                int(input_data.get("delinq_2yrs", 0)),
            )
            approval_prob = approval_data.get("approval_probability", 0)
            
            analytics.record_application(
                loan_amount=loan_amount,
                fico_score=fico_score,
                dti_ratio=dti_ratio,
                interest_rate=interest_rate,
                default_probability=prob_default,
                approval_probability=approval_prob,
                risk_level=risk_level,
                prediction=result["prediction"],
            )
        except Exception as e:
            logger.warning(f"Failed to record analytics: {e}")

        return result

    def _binary_safe_default_probs(self, proba: np.ndarray) -> tuple[float, float]:
        """Map `predict_proba` row to (safe, default) using `model.classes_` order."""
        classes = np.asarray(self.model.classes_)
        if classes.size != 2:
            raise ValueError(f"Expected a binary classifier; got classes={classes!r}")
        mask0 = classes == 0
        mask1 = classes == 1
        if not mask0.any() or not mask1.any():
            raise ValueError(f"Expected classes 0 and 1; got classes={classes!r}")
        idx_safe = int(np.flatnonzero(mask0)[0])
        idx_default = int(np.flatnonzero(mask1)[0])
        return float(proba[idx_safe]), float(proba[idx_default])

    def _validate_hard_rules(self, input_data: dict) -> dict | None:
        """Apply hard rejection rules for extremely risky profiles.
        
        Returns None if applicant passes validation, otherwise returns rejection response.
        """
        fico = input_data.get("fico_avg", 700)
        dti = input_data.get("dti", 0)
        delinq = input_data.get("delinq_2yrs", 0)
        emp_length = input_data.get("emp_length", 0)
        annual_inc = input_data.get("annual_inc", 0)
        loan_amnt = input_data.get("loan_amnt", 0)

        if _prediction_trace_logging():
            logger.debug(
                "validation inputs fico=%s dti=%s delinq=%s emp=%s income=%s loan=%s",
                fico,
                dti,
                delinq,
                emp_length,
                annual_inc,
                loan_amnt,
            )

        # Hard reject rules
        if fico < 500:
            return {
                "prediction": "DEFAULT_RISK",
                "default_probability": 0.95,
                "safe_probability": 0.05,
                "risk_level": "HIGH_RISK",
                "recommendation": "✗ Application REJECTED. FICO score below 500 (critical risk).",
                "confidence_score": 0.95,
            }

        if dti > 0.50:
            return {
                "prediction": "DEFAULT_RISK",
                "default_probability": 0.85,
                "safe_probability": 0.15,
                "risk_level": "HIGH_RISK",
                "recommendation": "✗ Application REJECTED. Debt-to-income ratio exceeds 50% (unsustainable).",
                "confidence_score": 0.90,
            }

        if delinq > 3:
            return {
                "prediction": "DEFAULT_RISK",
                "default_probability": 0.90,
                "safe_probability": 0.10,
                "risk_level": "HIGH_RISK",
                "recommendation": "✗ Application REJECTED. Delinquencies > 3 (high default history).",
                "confidence_score": 0.95,
            }

        if fico < 600 and dti > 0.40:
            return {
                "prediction": "DEFAULT_RISK",
                "default_probability": 0.80,
                "safe_probability": 0.20,
                "risk_level": "HIGH_RISK",
                "recommendation": "✗ Application REJECTED. Combined poor credit + high DTI.",
                "confidence_score": 0.88,
            }

        # Passed all hard rules
        return None

    def _get_java_recommendation(
        self, input_data: dict, prob_default: float, risk_level: str
    ) -> str:
        """Get recommendations from Java engine.
        
        Parameters
        ----------
        input_data : dict
            Original input data
        prob_default : float
            Predicted default probability
        risk_level : str
            Risk level classification
            
        Returns
        -------
        str
            Primary recommendation from Java engine
        """
        try:
            # Build request for Java engine
            java_request = {
                "loanAmount": input_data.get("loan_amnt", 0),
                "term": input_data.get("term", 60),
                "interestRate": input_data.get("int_rate", 0),
                "defaultProbability": prob_default,
                "riskLevel": risk_level,
                "ficoScore": input_data.get("fico_avg", 650),
                "dtiRatio": input_data.get("dti", 0),
                "annualIncome": input_data.get("annual_inc", 0),
            }

            # Call Java engine
            with httpx.Client(timeout=settings.java_engine_timeout_seconds) as client:
                response = client.post(settings.java_engine_url, json=java_request)
                response.raise_for_status()
                
                # Extract primary recommendation
                result = response.json()
                return result.get(
                    "primaryRecommendation",
                    "Recommendation generated. Please review loan details."
                )

        except Exception as e:
            logger.warning(f"Java engine call failed: {e}. Using fallback recommendation.")
            # Fallback to simple rule-based recommendation
            if risk_level == "LOW_RISK":
                return "✓ Loan approved. Low risk of default."
            elif risk_level == "MEDIUM_RISK":
                return "⚠ Loan requires review. Consider additional documentation or collateral."
            else:
                return "✗ Loan not recommended. High risk of default."

    def get_visualization_data(self, prediction_result: dict) -> dict:
        """Generate visualization data for prediction results.

        Parameters
        ----------
        prediction_result : dict
            Result from predict() method

        Returns
        -------
        dict
            Visualization-ready data including charts and metrics
        """
        prob_default = prediction_result.get("default_probability", 0)
        prob_safe = prediction_result.get("safe_probability", 1 - prob_default)
        risk_level = prediction_result.get("risk_level", "UNKNOWN")
        confidence = prediction_result.get("confidence_score", 0)

        # Risk gauge visualization data
        risk_colors = {
            "LOW_RISK": "#2ecc71",      # Green
            "MEDIUM_RISK": "#f39c12",   # Orange
            "HIGH_RISK": "#e74c3c",     # Red
        }

        viz_data = {
            "probability_chart": {
                "type": "pie",
                "data": {
                    "labels": ["Default Risk", "Safe"],
                    "datasets": [{
                        "data": [prob_default * 100, prob_safe * 100],
                        "backgroundColor": ["#e74c3c", "#2ecc71"],
                        "borderColor": ["#c0392b", "#27ae60"],
                        "borderWidth": 2
                    }]
                },
                "options": {
                    "responsive": True,
                    "plugins": {
                        "title": {"text": "Default Risk Probability"}
                    }
                }
            },
            "risk_gauge": {
                "type": "gauge",
                "value": prob_default,
                "color": risk_colors.get(risk_level, "#95a5a6"),
                "min": 0,
                "max": 1,
                "label": risk_level
            },
            "confidence_bar": {
                "type": "bar",
                "value": confidence * 100,
                "label": f"Confidence: {confidence * 100:.1f}%"
            },
            "metrics": {
                "default_probability": round(prob_default, 4),
                "safe_probability": round(prob_safe, 4),
                "risk_level": risk_level,
                "confidence_score": round(confidence, 4)
            }
        }
        return viz_data

    def batch_predict(self, input_data_list: list[dict]) -> list[dict]:
        """Make predictions for multiple loan applications.

        Parameters
        ----------
        input_data_list : list[dict]
            List of dictionaries with feature values

        Returns
        -------
        list[dict]
            List of prediction results
        """
        results = [self.predict(input_data) for input_data in input_data_list]
        
        # Add batch visualization summary
        viz_summary = self._generate_batch_visualization(results)
        
        return {
            "predictions": results,
            "visualization": viz_summary
        }

    def _generate_batch_visualization(self, predictions: list[dict]) -> dict:
        """Generate visualization summary for batch predictions."""
        if not predictions:
            return {}
        
        risk_counts = {
            "LOW_RISK": sum(1 for p in predictions if p.get("risk_level") == "LOW_RISK"),
            "MEDIUM_RISK": sum(1 for p in predictions if p.get("risk_level") == "MEDIUM_RISK"),
            "HIGH_RISK": sum(1 for p in predictions if p.get("risk_level") == "HIGH_RISK"),
        }
        
        avg_default_prob = np.mean([p.get("default_probability", 0) for p in predictions])
        
        return {
            "total_applications": len(predictions),
            "risk_distribution": risk_counts,
            "average_default_probability": round(avg_default_prob, 4),
            "approval_rate": round((risk_counts["LOW_RISK"] + risk_counts["MEDIUM_RISK"]) / len(predictions) * 100, 2),
            "chart_data": {
                "type": "bar",
                "labels": list(risk_counts.keys()),
                "datasets": [{
                    "label": "Application Count by Risk",
                    "data": list(risk_counts.values()),
                    "backgroundColor": ["#2ecc71", "#f39c12", "#e74c3c"]
                }]
            }
        }

    def get_feature_names(self) -> list[str]:
        """Get list of required feature names."""
        return self.feature_columns if self.feature_columns else []

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "model_type": type(self.model).__name__ if self.model else None,
            "feature_count": len(self.feature_columns) if self.feature_columns else 0,
            "is_loaded": self.is_loaded,
            "model_path": str(self.model_dir),
        }


# Global prediction service instance
_prediction_service: CreditDefaultPredictionService | None = None


def get_prediction_service() -> CreditDefaultPredictionService:
    """Get or create the global prediction service instance."""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = CreditDefaultPredictionService()
    return _prediction_service
