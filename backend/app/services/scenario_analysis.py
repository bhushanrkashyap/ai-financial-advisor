"""
What-If scenario analysis for credit predictions.
"""

import logging
import numpy as np
import pandas as pd
from pathlib import Path
import joblib

logger = logging.getLogger(__name__)


class ScenarioAnalysisService:
    """Service for what-if scenario analysis and sensitivity testing."""

    def __init__(self, model_dir: Path | None = None):
        """Initialize scenario analysis service.

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

            logger.info("✓ Scenario analysis service loaded")

        except Exception as e:
            logger.error(f"Failed to load artifacts: {e}")
            raise

    def _predict_proba(self, input_data: dict) -> float:
        """Helper to get default probability from input data."""
        df = pd.DataFrame([input_data])
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        df = df[self.feature_columns]
        df_scaled = self.scaler.transform(df)
        return float(self.model.predict_proba(df_scaled)[0, 1])

    def analyze_improvement_scenarios(self, input_data: dict) -> dict:
        """Generate improvement scenarios showing path to approval.

        Parameters
        ----------
        input_data : dict
            Current feature values

        Returns
        -------
        dict
            Scenarios showing how to improve approval chances
        """
        if not self.is_loaded:
            raise RuntimeError("Scenario service not loaded")

        try:
            current_prob = self._predict_proba(input_data)
            scenarios = {}

            # Scenario 1: Improve FICO Score
            fico_scenarios = self._scenario_fico_improvement(input_data, current_prob)
            scenarios["improve_fico"] = fico_scenarios

            # Scenario 2: Reduce DTI Ratio
            dti_scenarios = self._scenario_dti_reduction(input_data, current_prob)
            scenarios["reduce_dti"] = dti_scenarios

            # Scenario 3: Reduce Delinquencies (lower delinq_2yrs)
            delinq_scenarios = self._scenario_delinquency_reduction(input_data, current_prob)
            scenarios["reduce_delinquency"] = delinq_scenarios

            # Scenario 4: Increase Income
            income_scenarios = self._scenario_income_increase(input_data, current_prob)
            scenarios["increase_income"] = income_scenarios

            # Scenario 5: Reduce Loan Amount
            loan_scenarios = self._scenario_loan_reduction(input_data, current_prob)
            scenarios["reduce_loan"] = loan_scenarios

            # Best path to approval
            best_path = self._find_best_path(scenarios, current_prob)

            return {
                "current_probability": float(current_prob),
                "current_risk_level": self._risk_level(current_prob),
                "scenarios": scenarios,
                "best_path_to_approval": best_path,
                "approval_threshold": 0.3,  # Typically < 30% = low risk
            }

        except Exception as e:
            logger.error(f"Error analyzing scenarios: {e}")
            raise

    def _scenario_fico_improvement(self, input_data: dict, current_prob: float) -> list:
        """Generate FICO improvement scenarios."""
        scenarios = []
        current_fico = input_data.get("fico_avg", 700)

        for improvement in [20, 40, 60, 80]:
            new_fico = current_fico + improvement
            scenario_data = input_data.copy()
            scenario_data["fico_avg"] = new_fico

            new_prob = self._predict_proba(scenario_data)
            prob_reduction = (current_prob - new_prob) / current_prob * 100 if current_prob > 0 else 0

            scenarios.append({
                "action": f"Improve FICO score by {improvement} points",
                "from_value": current_fico,
                "to_value": new_fico,
                "new_probability": float(new_prob),
                "probability_reduction": float(prob_reduction),
                "effort": self._assess_effort("FICO", improvement),
                "timeframe": "3-6 months"
            })

        return scenarios

    def _scenario_dti_reduction(self, input_data: dict, current_prob: float) -> list:
        """Generate DTI reduction scenarios."""
        scenarios = []
        current_dti = input_data.get("dti", 0.3)

        for new_dti in [0.20, 0.25, 0.30, 0.35]:
            if new_dti < current_dti:
                scenario_data = input_data.copy()
                scenario_data["dti"] = new_dti

                new_prob = self._predict_proba(scenario_data)
                prob_reduction = (current_prob - new_prob) / current_prob * 100 if current_prob > 0 else 0

                scenarios.append({
                    "action": f"Reduce debt-to-income ratio to {new_dti:.1%}",
                    "from_value": current_dti,
                    "to_value": new_dti,
                    "new_probability": float(new_prob),
                    "probability_reduction": float(prob_reduction),
                    "effort": self._assess_effort("DTI", (current_dti - new_dti)),
                    "method": "Pay down existing debts"
                })

        return scenarios

    def _scenario_delinquency_reduction(self, input_data: dict, current_prob: float) -> list:
        """Generate delinquency reduction scenarios."""
        scenarios = []
        current_delinq = input_data.get("delinq_2yrs", 0)

        if current_delinq > 0:
            for new_delinq in range(int(current_delinq) - 1, -1, -1):
                scenario_data = input_data.copy()
                scenario_data["delinq_2yrs"] = new_delinq

                new_prob = self._predict_proba(scenario_data)
                prob_reduction = (current_prob - new_prob) / current_prob * 100 if current_prob > 0 else 0

                scenarios.append({
                    "action": f"Clear delinquencies (reduce to {new_delinq})",
                    "from_value": int(current_delinq),
                    "to_value": new_delinq,
                    "new_probability": float(new_prob),
                    "probability_reduction": float(prob_reduction),
                    "effort": "MEDIUM",
                    "impact": "Improves credit history"
                })

        return scenarios

    def _scenario_income_increase(self, input_data: dict, current_prob: float) -> list:
        """Generate income increase scenarios."""
        scenarios = []
        current_income = input_data.get("annual_inc", 50000)

        for percent_increase in [10, 20, 30, 50]:
            new_income = current_income * (1 + percent_increase / 100)
            scenario_data = input_data.copy()
            scenario_data["annual_inc"] = new_income

            # Also adjust DTI if loan amount is fixed
            if "dti" in scenario_data:
                loan_amnt = input_data.get("loan_amnt", 25000)
                new_dti = (loan_amnt * 12 / 100) / new_income  # Approximate
                scenario_data["dti"] = min(new_dti, 0.5)

            new_prob = self._predict_proba(scenario_data)
            prob_reduction = (current_prob - new_prob) / current_prob * 100 if current_prob > 0 else 0

            scenarios.append({
                "action": f"Increase annual income by {percent_increase}%",
                "from_value": int(current_income),
                "to_value": int(new_income),
                "new_probability": float(new_prob),
                "probability_reduction": float(prob_reduction),
                "effort": "HIGH",
                "timeframe": "6-12 months"
            })

        return scenarios

    def _scenario_loan_reduction(self, input_data: dict, current_prob: float) -> list:
        """Generate loan amount reduction scenarios."""
        scenarios = []
        current_loan = input_data.get("loan_amnt", 25000)

        for reduction_pct in [10, 20, 30, 50]:
            new_loan = current_loan * (1 - reduction_pct / 100)
            scenario_data = input_data.copy()
            scenario_data["loan_amnt"] = new_loan

            # Adjust installment
            term_months = input_data.get("term", 60) / 12
            int_rate = input_data.get("int_rate", 10) / 12 / 100
            if int_rate > 0:
                monthly_payment = new_loan * (int_rate * (1 + int_rate) ** (term_months * 12)) / ((1 + int_rate) ** (term_months * 12) - 1)
                scenario_data["installment"] = monthly_payment

            new_prob = self._predict_proba(scenario_data)
            prob_reduction = (current_prob - new_prob) / current_prob * 100 if current_prob > 0 else 0

            scenarios.append({
                "action": f"Reduce loan amount by {reduction_pct}%",
                "from_value": int(current_loan),
                "to_value": int(new_loan),
                "new_probability": float(new_prob),
                "probability_reduction": float(prob_reduction),
                "effort": "LOW",
                "impact": "Reduces default risk through lower obligation"
            })

        return scenarios

    def _find_best_path(self, scenarios: dict, current_prob: float) -> dict:
        """Find the most effective and achievable path to approval."""
        best_scenarios = []

        for scenario_type, scenario_list in scenarios.items():
            for scenario in scenario_list:
                if scenario["new_probability"] < 0.3:  # Approval threshold
                    best_scenarios.append({
                        "type": scenario_type,
                        "action": scenario["action"],
                        "final_probability": scenario["new_probability"],
                        "effort": scenario.get("effort", "UNKNOWN"),
                        "impact": scenario["probability_reduction"]
                    })

        # Sort by effort (LOW, MEDIUM, HIGH)
        effort_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        best_scenarios.sort(key=lambda x: effort_order.get(x["effort"], 999))

        return {
            "quick_wins": [s for s in best_scenarios if s["effort"] == "LOW"][:3],
            "medium_term": [s for s in best_scenarios if s["effort"] == "MEDIUM"][:3],
            "long_term": [s for s in best_scenarios if s["effort"] == "HIGH"][:3],
            "recommended_action": best_scenarios[0]["action"] if best_scenarios else "Reapply after improving credit profile"
        }

    def _assess_effort(self, factor: str, amount: float) -> str:
        """Assess effort required for improvement."""
        if factor == "FICO":
            if amount <= 20:
                return "LOW"
            elif amount <= 60:
                return "MEDIUM"
            else:
                return "HIGH"
        elif factor == "DTI":
            if amount <= 0.05:
                return "LOW"
            elif amount <= 0.15:
                return "MEDIUM"
            else:
                return "HIGH"
        return "MEDIUM"

    def _risk_level(self, prob: float) -> str:
        """Determine risk level from probability."""
        if prob < 0.3:
            return "LOW_RISK"
        elif prob < 0.6:
            return "MEDIUM_RISK"
        else:
            return "HIGH_RISK"


# Global scenario service instance
_scenario_service: ScenarioAnalysisService | None = None


def get_scenario_analysis_service() -> ScenarioAnalysisService:
    """Get or create the global scenario analysis service instance."""
    global _scenario_service
    if _scenario_service is None:
        _scenario_service = ScenarioAnalysisService()
    return _scenario_service
