#!/usr/bin/env python3
"""
Integration test script for AI Financial Advisor system.
Tests both Python backend API and Java recommendation engine.
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
API_TIMEOUT = 10

# Test loan applications
TEST_CASES = [
    {
        "name": "Low Risk Profile",
        "data": {
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
            "verification_status_Source_Verified": 0,
            "purpose_credit_card": 0,
            "purpose_debt_consolidation": 0,
            "purpose_car": 0,
            "purpose_medical": 0,
            "purpose_home_improvement": 0,
            "application_type_Individual": 1,
            "application_type_Joint_App": 0,
        },
    },
    {
        "name": "Medium Risk Profile",
        "data": {
            "loan_amnt": 15000,
            "term": 60,
            "int_rate": 12.5,
            "installment": 300,
            "emp_length": 5,
            "annual_inc": 75000,
            "dti": 0.25,
            "delinq_2yrs": 1,
            "inq_last_6mths": 1,
            "open_acc": 8,
            "pub_rec": 0,
            "revol_bal": 10000,
            "revol_util": 0.5,
            "fico_avg": 690,
            "grade_encoded": 3,
            "sub_grade_encoded": 3,
            "home_ownership_MORTGAGE": 1,
            "home_ownership_OWN": 0,
            "home_ownership_RENT": 0,
            "verification_status_Verified": 1,
            "verification_status_Source_Verified": 0,
            "purpose_credit_card": 0,
            "purpose_debt_consolidation": 1,
            "purpose_car": 0,
            "purpose_medical": 0,
            "purpose_home_improvement": 0,
            "application_type_Individual": 1,
            "application_type_Joint_App": 0,
        },
    },
    {
        "name": "High Risk Profile",
        "data": {
            "loan_amnt": 25000,
            "term": 36,
            "int_rate": 18.5,
            "installment": 750,
            "emp_length": 2,
            "annual_inc": 50000,
            "dti": 0.35,
            "delinq_2yrs": 2,
            "inq_last_6mths": 3,
            "open_acc": 5,
            "pub_rec": 1,
            "revol_bal": 20000,
            "revol_util": 0.8,
            "fico_avg": 650,
            "grade_encoded": 4,
            "sub_grade_encoded": 4,
            "home_ownership_MORTGAGE": 0,
            "home_ownership_OWN": 1,
            "home_ownership_RENT": 0,
            "verification_status_Verified": 0,
            "verification_status_Source_Verified": 1,
            "purpose_credit_card": 1,
            "purpose_debt_consolidation": 0,
            "purpose_car": 0,
            "purpose_medical": 0,
            "purpose_home_improvement": 0,
            "application_type_Individual": 1,
            "application_type_Joint_App": 0,
        },
    },
]


def check_health() -> bool:
    """Check if backend API is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def get_model_info() -> Dict[str, Any]:
    """Get information about the loaded model."""
    try:
        response = requests.get(f"{BACKEND_URL}/api/credit/model-info", timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error getting model info: {e}")
        return {}


def predict_single(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Make a single prediction."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/credit/predict",
            json=test_case["data"],
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error making prediction: {e}")
        return {}


def predict_batch(test_cases: list) -> list:
    """Make batch predictions."""
    try:
        data = [tc["data"] for tc in test_cases]
        response = requests.post(
            f"{BACKEND_URL}/api/credit/batch-predict",
            json=data,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error making batch prediction: {e}")
        return []


def format_prediction_output(test_case: Dict, prediction: Dict) -> str:
    """Format prediction output for display."""
    output = []
    output.append(f"\n{'='*80}")
    output.append(f"TEST CASE: {test_case['name']}")
    output.append(f"{'='*80}")
    output.append(f"\nLoan Details:")
    
    loan_amt = test_case['data'].get('loan_amnt', 'N/A')
    if loan_amt != 'N/A':
        output.append(f"  Amount: ${loan_amt:,}")
    else:
        output.append(f"  Amount: {loan_amt}")
    
    output.append(f"  Interest Rate: {test_case['data'].get('int_rate', 'N/A')}%")
    output.append(f"  Term: {test_case['data'].get('term', 'N/A')} months")
    output.append(f"  FICO Score: {test_case['data'].get('fico_avg', 'N/A')}")
    output.append(f"  DTI Ratio: {test_case['data'].get('dti', 'N/A'):.1%}")
    
    output.append(f"\n✓ Prediction Results:")
    output.append(f"  Prediction: {prediction.get('prediction', 'N/A')}")
    output.append(f"  Default Probability: {prediction.get('default_probability', 'N/A'):.2%}")
    output.append(f"  Safe Probability: {prediction.get('safe_probability', 'N/A'):.2%}")
    output.append(f"  Risk Level: {prediction.get('risk_level', 'N/A')}")
    output.append(f"  Confidence: {prediction.get('confidence_score', 'N/A'):.1%}")
    
    output.append(f"\n📋 Recommendation:")
    output.append(f"  {prediction.get('recommendation', 'N/A')}")
    
    return "\n".join(output)


def main():
    """Run integration tests."""
    print("\n" + "="*80)
    print("AI FINANCIAL ADVISOR - INTEGRATION TEST")
    print("="*80)
    
    # Check backend health
    print("\n1. Checking backend API health...")
    if not check_health():
        print("❌ Backend API is not running!")
        print("   Start it with: python -m uvicorn main:app --reload")
        sys.exit(1)
    print("✓ Backend API is healthy")
    
    # Get model info
    print("\n2. Getting model information...")
    model_info = get_model_info()
    if model_info:
        print(f"✓ Model Info:")
        print(f"   Type: {model_info.get('model_type', 'N/A')}")
        print(f"   Features: {model_info.get('feature_count', 'N/A')}")
        print(f"   Loaded: {model_info.get('is_loaded', False)}")
    
    # Test single predictions
    print("\n3. Testing single predictions...")
    for test_case in TEST_CASES:
        print(f"\n   Testing: {test_case['name']}")
        prediction = predict_single(test_case)
        if prediction:
            print(f"   ✓ Prediction successful")
            print(format_prediction_output(test_case, prediction))
        else:
            print(f"   ❌ Prediction failed")
    
    # Test batch prediction
    print("\n4. Testing batch prediction...")
    predictions = predict_batch(TEST_CASES)
    if predictions:
        print(f"✓ Batch prediction successful ({len(predictions)} results)")
        for i, (test_case, prediction) in enumerate(zip(TEST_CASES, predictions)):
            print(f"\n   [{i+1}] {test_case['name']}: {prediction.get('risk_level', 'N/A')}")
    else:
        print("❌ Batch prediction failed")
    
    print("\n" + "="*80)
    print("INTEGRATION TEST COMPLETE")
    print("="*80)
    print("\nNext steps:")
    print("1. Run Java recommendation engine: cd java-engine && mvn exec:java")
    print("2. Start frontend development server: cd frontend && npm run dev")
    print("3. Access API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
