"""
Fairness and bias analysis service for credit default predictions.
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)


class FairnessService:
    """Service for analyzing fairness and bias in model predictions."""

    def __init__(self, model_dir: Path | None = None):
        """Initialize fairness analysis service.

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
        self.is_loaded = False

        self._load_artifacts()

    def _load_artifacts(self) -> None:
        """Load model artifacts."""
        try:
            model_path = self.model_dir / "best_credit_default_model.pkl"
            scaler_path = self.model_dir / "logistic_scaler.pkl"
            features_path = self.model_dir / "feature_columns.pkl"

            if not all([model_path.exists(), scaler_path.exists(), features_path.exists()]):
                raise FileNotFoundError("Missing model artifacts")

            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
            self.feature_columns = joblib.load(features_path)
            self.is_loaded = True

            logger.info("✓ Fairness service loaded")

        except Exception as e:
            logger.error(f"Failed to load artifacts: {e}")
            raise

    def analyze_prediction_fairness(self, predictions_list: list[dict]) -> dict:
        """Analyze fairness across different demographic groups.

        Parameters
        ----------
        predictions_list : list[dict]
            List of predictions with demographic information

        Returns
        -------
        dict
            Fairness metrics and bias analysis
        """
        if not self.is_loaded:
            raise RuntimeError("Fairness service not loaded")

        try:
            df = pd.DataFrame(predictions_list)

            # Detect demographic columns
            demographic_cols = [
                col for col in df.columns 
                if any(x in col.lower() for x in ['age', 'gender', 'race', 'married', 'home', 'employment'])
            ]

            fairness_metrics = {}

            for demo_col in demographic_cols:
                if demo_col not in df.columns:
                    continue

                groups = df[demo_col].unique()
                group_metrics = {}

                for group in groups:
                    group_data = df[df[demo_col] == group]
                    
                    approval_rate = (1 - group_data.get("default_probability", [1]).mean()) * 100
                    avg_default_prob = group_data.get("default_probability", [0]).mean()
                    count = len(group_data)

                    group_metrics[str(group)] = {
                        "approval_rate": float(approval_rate),
                        "average_default_probability": float(avg_default_prob),
                        "sample_size": int(count),
                        "recommended_interest_rate_adjustment": self._calc_rate_adjustment(avg_default_prob)
                    }

                fairness_metrics[demo_col] = group_metrics

            # Calculate disparate impact ratio
            disparate_impact = self._calculate_disparate_impact(fairness_metrics)

            # Bias score (0 = fair, 1 = biased)
            bias_score = self._calculate_bias_score(fairness_metrics)

            return {
                "fairness_metrics": fairness_metrics,
                "disparate_impact_ratio": disparate_impact,
                "bias_score": float(bias_score),
                "bias_level": self._assess_bias_level(bias_score),
                "recommendations": self._generate_fairness_recommendations(fairness_metrics, bias_score)
            }

        except Exception as e:
            logger.error(f"Error analyzing fairness: {e}")
            raise

    def analyze_single_prediction_fairness(self, input_data: dict, group_key: str = None) -> dict:
        """Analyze fairness aspects of a single prediction.

        Parameters
        ----------
        input_data : dict
            Feature values
        group_key : str, optional
            Demographic group identifier

        Returns
        -------
        dict
            Fairness analysis for single prediction
        """
        if not self.is_loaded:
            raise RuntimeError("Fairness service not loaded")

        try:
            # Prepare data
            df = pd.DataFrame([input_data])
            for col in self.feature_columns:
                if col not in df.columns:
                    df[col] = 0
            df = df[self.feature_columns]
            df_scaled = self.scaler.transform(df)

            # Get prediction
            pred_proba = self.model.predict_proba(df_scaled)[0]
            default_prob = pred_proba[1]

            # Fairness checks
            fico = input_data.get("fico_avg", 700)
            income = input_data.get("annual_inc", 50000)

            fairness_checks = {
                "fico_discrimination_flag": fico < 600 and default_prob > 0.7,  # Very low score = high rejection
                "income_bias_flag": income < 30000 and default_prob > 0.75,  # Low income = likely rejection
                "dti_fairness": input_data.get("dti", 0.3) > 0.4,  # High DTI might discriminate
                "employment_risk": input_data.get("emp_length", 0) < 1,  # Low employment risk
            }

            return {
                "group_key": group_key,
                "default_probability": float(default_prob),
                "fairness_checks": fairness_checks,
                "potential_disparate_impact": any(fairness_checks.values()),
                "discrimination_risk_level": self._assess_discrimination_risk(fairness_checks),
                "fairness_recommendation": self._recommend_adjustment(fairness_checks)
            }

        except Exception as e:
            logger.error(f"Error in fairness analysis: {e}")
            raise

    def _calc_rate_adjustment(self, default_prob: float) -> float:
        """Calculate interest rate adjustment based on default probability.

        Parameters
        ----------
        default_prob : float
            Default probability (0-1)

        Returns
        -------
        float
            Recommended rate adjustment in basis points
        """
        if default_prob < 0.1:
            return 0.0  # No adjustment
        elif default_prob < 0.3:
            return 1.0  # +100 bps
        elif default_prob < 0.5:
            return 2.0  # +200 bps
        else:
            return 3.0  # +300 bps

    def _calculate_disparate_impact(self, fairness_metrics: dict) -> dict:
        """Calculate disparate impact ratios.

        Parameters
        ----------
        fairness_metrics : dict
            Fairness metrics by demographic group

        Returns
        -------
        dict
            Disparate impact analysis
        """
        disparate_impact = {}

        for demo_col, groups in fairness_metrics.items():
            approval_rates = [g["approval_rate"] for g in groups.values()]
            
            if approval_rates:
                min_rate = min(approval_rates)
                max_rate = max(approval_rates)
                
                # 80% rule: disparate impact ratio > 0.8 indicates fairness
                if min_rate > 0:
                    ratio = min_rate / max_rate
                    disparate_impact[demo_col] = {
                        "ratio": float(ratio),
                        "is_fair": ratio >= 0.8,
                        "gap_percent": float(max_rate - min_rate)
                    }

        return disparate_impact

    def _calculate_bias_score(self, fairness_metrics: dict) -> float:
        """Calculate overall bias score (0 = fair, 1 = biased)."""
        if not fairness_metrics:
            return 0.0

        bias_scores = []

        for demo_col, groups in fairness_metrics.items():
            approval_rates = [g["approval_rate"] for g in groups.values()]
            
            if len(approval_rates) > 1:
                # High variance = high bias
                variance = np.var(approval_rates)
                # Normalize to 0-1
                normalized_bias = min(1.0, variance / 100)
                bias_scores.append(normalized_bias)

        return float(np.mean(bias_scores)) if bias_scores else 0.0

    def _assess_bias_level(self, bias_score: float) -> str:
        """Assess bias level from score."""
        if bias_score < 0.1:
            return "FAIR"
        elif bias_score < 0.3:
            return "MINOR_BIAS"
        elif bias_score < 0.6:
            return "MODERATE_BIAS"
        else:
            return "SEVERE_BIAS"

    def _assess_discrimination_risk(self, fairness_checks: dict) -> str:
        """Assess discrimination risk level."""
        risk_count = sum(fairness_checks.values())
        
        if risk_count == 0:
            return "LOW"
        elif risk_count == 1:
            return "MEDIUM"
        elif risk_count == 2:
            return "HIGH"
        else:
            return "CRITICAL"

    def _recommend_adjustment(self, fairness_checks: dict) -> str:
        """Generate fairness recommendation."""
        if not any(fairness_checks.values()):
            return "✓ Prediction appears fair. Proceed with standard approval."
        
        issues = [k.replace("_", " ") for k, v in fairness_checks.items() if v]
        return f"⚠ Potential fairness issues detected: {', '.join(issues)}. Consider manual review."

    def _generate_fairness_recommendations(self, fairness_metrics: dict, bias_score: float) -> list:
        """Generate fairness recommendations."""
        recommendations = []

        if bias_score > 0.3:
            recommendations.append("Review demographic disparities in approval rates")
            recommendations.append("Consider alternative credit models with bias mitigation")

        for demo_col, groups in fairness_metrics.items():
            approval_rates = [g["approval_rate"] for g in groups.values()]
            if approval_rates and max(approval_rates) - min(approval_rates) > 20:
                recommendations.append(f"High variance in approval rates across {demo_col} groups")

        if not recommendations:
            recommendations.append("✓ Model shows fair lending practices")

        return recommendations


# Global fairness service instance
_fairness_service: FairnessService | None = None


def get_fairness_service() -> FairnessService:
    """Get or create the global fairness service instance."""
    global _fairness_service
    if _fairness_service is None:
        _fairness_service = FairnessService()
    return _fairness_service
