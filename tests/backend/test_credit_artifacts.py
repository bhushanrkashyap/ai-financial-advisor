"""Consistency checks between training artifacts, schema, and inference."""

from __future__ import annotations

from pathlib import Path

import joblib
import pytest

REPO = Path(__file__).resolve().parents[2]
MODELS = REPO / "backend" / "models"


@pytest.mark.skipif(
    not (MODELS / "feature_columns.pkl").is_file(),
    reason="feature_columns.pkl not present",
)
def test_feature_columns_match_scaler_order() -> None:
    scaler = joblib.load(MODELS / "logistic_scaler.pkl")
    features = joblib.load(MODELS / "feature_columns.pkl")
    expected = list(scaler.feature_names_in_)
    assert features == expected
    assert "application_type_Joint App" in features
    assert "verification_status_Source Verified" in features


def test_loan_input_model_dump_uses_training_column_names() -> None:
    from app.schemas.credit import LoanApplicationInput

    app = LoanApplicationInput(
        loan_amnt=15000,
        term=60,
        int_rate=12.5,
        installment=300,
        emp_length=5,
        annual_inc=75000,
        dti=0.25,
        fico_avg=690,
        grade_encoded=3,
        sub_grade_encoded=3,
        application_type_Joint_App=1,
        verification_status_Source_Verified=1,
    )
    payload = app.model_dump(by_alias=True)
    assert payload.get("application_type_Joint App") == 1
    assert payload.get("verification_status_Source Verified") == 1
    assert "application_type_Joint_App" not in payload


@pytest.mark.skipif(
    not all(
        (MODELS / n).is_file()
        for n in ("best_credit_default_model.pkl", "logistic_scaler.pkl", "feature_columns.pkl")
    ),
    reason="model artifacts incomplete",
)
def test_prediction_service_loads_and_scores() -> None:
    from app.services.prediction import CreditDefaultPredictionService

    svc = CreditDefaultPredictionService(model_dir=MODELS)
    assert svc.is_loaded
    low = {
        "loan_amnt": 5000,
        "term": 36,
        "int_rate": 7.5,
        "installment": 150,
        "emp_length": 10,
        "annual_inc": 120000,
        "dti": 0.15,
        "delinq_2yrs": 0,
        "inq_last_6mths": 0,
        "open_acc": 12,
        "pub_rec": 0,
        "revol_bal": 5000,
        "revol_util": 0.3,
        "fico_avg": 720,
        "grade_encoded": 2,
        "sub_grade_encoded": 2,
        "home_ownership_MORTGAGE": 1,
        "home_ownership_OWN": 0,
        "home_ownership_RENT": 0,
        "verification_status_Verified": 1,
        "verification_status_Source Verified": 0,
        "purpose_credit_card": 0,
        "purpose_debt_consolidation": 0,
        "purpose_car": 0,
        "purpose_medical": 0,
        "purpose_home_improvement": 0,
        "application_type_Individual": 1,
        "application_type_Joint App": 0,
    }
    out = svc.predict(low)
    assert out["prediction"] in ("SAFE", "DEFAULT_RISK")
    assert 0 <= out["default_probability"] <= 1
    assert abs(out["default_probability"] + out["safe_probability"] - 1.0) < 1e-5
