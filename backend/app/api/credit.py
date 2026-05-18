"""
API endpoints for credit default prediction.
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.credit import (
    CreditPredictionResponse,
    HealthResponse,
    LoanApplicationInput,
)
from app.services.prediction import get_prediction_service
from app.services.explainability import get_explainability_service
from app.services.fairness import get_fairness_service
from app.services.scenario_analysis import get_scenario_analysis_service

logger = logging.getLogger(__name__)

credit_router = APIRouter(prefix="/credit", tags=["credit"])


@credit_router.post(
    "/predict",
    response_model=CreditPredictionResponse,
    summary="Predict credit default risk",
    description="Analyzes a loan application and predicts the probability of default.",
)
async def predict_credit_default(application: LoanApplicationInput) -> CreditPredictionResponse:
    """Predict credit default risk for a loan application.

    Parameters
    ----------
    application : LoanApplicationInput
        Loan application details

    Returns
    -------
    CreditPredictionResponse
        Prediction results including default probability and risk level

    Raises
    ------
    HTTPException
        If the model is not loaded or prediction fails
    """
    try:
        service = get_prediction_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Prediction model not loaded. Please try again later.",
            )

        # Align keys with training CSV / feature_columns.pkl (spaces in some one-hot names)
        input_data = application.model_dump(by_alias=True)

        # Get prediction
        result = service.predict(input_data)

        return CreditPredictionResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        ) from e


@credit_router.post(
    "/batch-predict",
    response_model=list[CreditPredictionResponse],
    summary="Batch predict credit default risk",
    description="Analyzes multiple loan applications and predicts default probability for each.",
)
async def batch_predict_credit_default(
    applications: list[LoanApplicationInput],
) -> list[CreditPredictionResponse]:
    """Predict credit default risk for multiple loan applications.

    Parameters
    ----------
    applications : list[LoanApplicationInput]
        List of loan applications

    Returns
    -------
    list[CreditPredictionResponse]
        List of prediction results

    Raises
    ------
    HTTPException
        If the model is not loaded or prediction fails
    """
    try:
        if not applications:
            raise HTTPException(
                status_code=400,
                detail="At least one application is required",
            )

        if len(applications) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Maximum 1000 applications per batch request",
            )

        service = get_prediction_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Prediction model not loaded. Please try again later.",
            )

        # Convert to list of dicts (training column names)
        input_data_list = [app.model_dump(by_alias=True) for app in applications]

        # Get predictions
        results = service.batch_predict(input_data_list)

        return [CreditPredictionResponse(**result) for result in results]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch prediction failed: {str(e)}",
        ) from e


@credit_router.get(
    "/model-info",
    summary="Get model information",
    description="Returns information about the loaded prediction model.",
)
async def get_model_info() -> dict:
    """Get information about the prediction model.

    Returns
    -------
    dict
        Model metadata including type, feature count, and status
    """
    try:
        service = get_prediction_service()
        return service.get_model_info()
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve model information",
        ) from e


@credit_router.get(
    "/features",
    response_model=list[str],
    summary="Get required features",
    description="Returns the list of required features for predictions.",
)
async def get_required_features() -> list[str]:
    """Get list of required features for prediction.

    Returns
    -------
    list[str]
        List of feature names in required order

    Raises
    ------
    HTTPException
        If features cannot be retrieved
    """
    try:
        service = get_prediction_service()
        features = service.get_feature_names()
        if not features:
            raise HTTPException(
                status_code=503,
                detail="Model features not loaded",
            )
        return features
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting features: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve features",
        ) from e


@credit_router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check for credit service",
    description="Checks if the credit prediction service is ready.",
)
async def health_check() -> HealthResponse:
    """Health check for the credit prediction service.

    Returns
    -------
    HealthResponse
        Health status and model availability
    """
    service = get_prediction_service()
    return HealthResponse(
        status="healthy" if service.is_loaded else "unhealthy",
        model_loaded=service.is_loaded,
        version="0.1.0",
    )


@credit_router.post(
    "/predict-with-visualization",
    summary="Predict credit default with visualization data",
    description="Analyzes a loan application and returns prediction with visualization data.",
)
async def predict_with_visualization(application: LoanApplicationInput) -> dict:
    """Predict credit default risk and return visualization data.

    Parameters
    ----------
    application : LoanApplicationInput
        Loan application details

    Returns
    -------
    dict
        Prediction results with visualization data (charts, gauges, etc.)

    Raises
    ------
    HTTPException
        If the model is not loaded or prediction fails
    """
    try:
        service = get_prediction_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Prediction model not loaded. Please try again later.",
            )

        input_data = application.model_dump(by_alias=True)
        prediction = service.predict(input_data)
        viz_data = service.get_visualization_data(prediction)

        return {
            "prediction": prediction,
            "visualization": viz_data
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting with visualization: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to make prediction",
        ) from e


@credit_router.post(
    "/batch-predict-with-visualization",
    summary="Batch predict with visualization",
    description="Analyzes multiple loan applications and returns batch visualization summary.",
)
async def batch_predict_with_visualization(applications: list[LoanApplicationInput]) -> dict:
    """Batch predict credit default risk with summary visualization.

    Parameters
    ----------
    applications : list[LoanApplicationInput]
        List of loan applications

    Returns
    -------
    dict
        Batch predictions with summary visualization

    Raises
    ------
    HTTPException
        If the model is not loaded or prediction fails
    """
    try:
        service = get_prediction_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Prediction model not loaded. Please try again later.",
            )

        input_data_list = [app.model_dump(by_alias=True) for app in applications]
        results = service.batch_predict(input_data_list)

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error batch predicting: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process batch predictions",
        ) from e


# ============= EXPLAINABILITY ENDPOINTS =============


@credit_router.post(
    "/explain",
    summary="Get SHAP-based prediction explanation",
    description="Returns detailed SHAP values showing which features contributed to the prediction.",
)
async def explain_prediction(application: LoanApplicationInput) -> dict:
    """Explain prediction using SHAP values.

    Parameters
    ----------
    application : LoanApplicationInput
        Loan application details

    Returns
    -------
    dict
        SHAP values, feature importance, and explanation summary
    """
    try:
        service = get_explainability_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Explainability service not ready.",
            )

        input_data = application.model_dump(by_alias=True)
        explanation = service.explain_prediction(input_data, num_features=10)

        return {
            "status": "success",
            "explanation": explanation
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate explanation",
        ) from e


@credit_router.post(
    "/feature-impact",
    summary="Analyze impact of changing a feature",
    description="Shows how changing a specific feature value affects the prediction.",
)
async def analyze_feature_impact(application: LoanApplicationInput, feature_name: str, new_value: float) -> dict:
    """Analyze impact of changing a feature value.

    Parameters
    ----------
    application : LoanApplicationInput
        Original loan application
    feature_name : str
        Feature to modify
    new_value : float
        New value for the feature

    Returns
    -------
    dict
        Impact analysis showing probability change
    """
    try:
        service = get_explainability_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Explainability service not ready.",
            )

        input_data = application.model_dump(by_alias=True)
        impact = service.get_feature_impact(feature_name, new_value, input_data)

        return {
            "status": "success",
            "feature_impact": impact
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing feature impact: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze feature impact",
        ) from e


# ============= FAIRNESS ENDPOINTS =============


@credit_router.post(
    "/analyze-fairness",
    summary="Analyze fairness and bias in prediction",
    description="Checks for potential bias and fairness issues in the prediction.",
)
async def analyze_fairness(application: LoanApplicationInput) -> dict:
    """Analyze fairness aspects of a prediction.

    Parameters
    ----------
    application : LoanApplicationInput
        Loan application details

    Returns
    -------
    dict
        Fairness metrics and bias assessment
    """
    try:
        service = get_fairness_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Fairness service not ready.",
            )

        input_data = application.model_dump(by_alias=True)
        fairness_result = service.analyze_single_prediction_fairness(input_data)

        return {
            "status": "success",
            "fairness_analysis": fairness_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing fairness: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze fairness",
        ) from e


# ============= WHAT-IF SCENARIO ENDPOINTS =============


@credit_router.post(
    "/scenarios",
    summary="Generate what-if improvement scenarios",
    description="Shows paths to approval by improving various factors.",
)
async def analyze_scenarios(application: LoanApplicationInput) -> dict:
    """Analyze what-if improvement scenarios.

    Parameters
    ----------
    application : LoanApplicationInput
        Current loan application

    Returns
    -------
    dict
        Improvement scenarios and paths to approval
    """
    try:
        service = get_scenario_analysis_service()

        if not service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Scenario analysis service not ready.",
            )

        input_data = application.model_dump(by_alias=True)
        scenarios = service.analyze_improvement_scenarios(input_data)

        return {
            "status": "success",
            "scenarios": scenarios
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing scenarios: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze scenarios",
        ) from e


# ============= FINANCIAL CALCULATION ENDPOINTS =============


@credit_router.post(
    "/calculate-emi",
    summary="Calculate EMI and financial breakdowns",
    description="Calculates monthly EMI and financial metrics for a loan.",
)
async def calculate_emi(
    loan_amount: float,
    interest_rate: float,
    term_months: int,
) -> dict:
    """Calculate EMI and financial metrics.

    Parameters
    ----------
    loan_amount : float
        Loan amount in USD
    interest_rate : float
        Annual interest rate (%)
    term_months : int
        Loan term in months

    Returns
    -------
    dict
        EMI calculation details
    """
    try:
        from app.services.financial_calculator import get_financial_calculator
        
        if loan_amount <= 0 or term_months <= 0 or interest_rate < 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid loan parameters",
            )

        calculator = get_financial_calculator()
        emi_data = calculator.calculate_emi(loan_amount, interest_rate, term_months)

        return {
            "monthly_emi": emi_data.monthly_emi,
            "total_amount_payable": emi_data.total_amount_payable,
            "total_interest": emi_data.total_interest,
            "principal": emi_data.principal,
            "term_months": emi_data.term_months,
            "annual_interest_rate": emi_data.annual_interest_rate,
            "monthly_interest_rate": emi_data.monthly_interest_rate,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating EMI: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate EMI",
        ) from e


@credit_router.post(
    "/financial-summary",
    summary="Get complete financial summary",
    description="Returns comprehensive financial analysis including EMI, health metrics, and recommendations.",
)
async def get_financial_summary(application: LoanApplicationInput) -> dict:
    """Get complete financial summary for an application.

    Parameters
    ----------
    application : LoanApplicationInput
        Loan application details

    Returns
    -------
    dict
        Complete financial analysis
    """
    try:
        from app.services.financial_calculator import get_financial_calculator
        from app.services.prediction import get_prediction_service
        
        calculator = get_financial_calculator()
        pred_service = get_prediction_service()

        input_data = application.model_dump(by_alias=True)

        # Get prediction first
        prediction = pred_service.predict(input_data)

        # Calculate EMI
        emi_data = calculator.calculate_emi(
            application.loan_amnt,
            application.int_rate,
            application.term,
        )

        # Calculate financial health
        health = calculator.calculate_financial_health(
            application.annual_inc,
            emi_data.monthly_emi,
            employment_years=application.emp_length,
            delinquencies=application.delinq_2yrs,
        )

        # Calculate approval probability
        approval_score = calculator.calculate_approval_probability_score(
            prediction["default_probability"],
            application.dti,
            application.fico_avg,
            application.emp_length,
            application.delinq_2yrs,
        )

        # Get recommendations
        recommendations = calculator.calculate_improvement_recommendations(
            application.fico_avg,
            application.dti,
            application.delinq_2yrs,
            application.emp_length,
            prediction["default_probability"],
        )

        return {
            "loan_amount": application.loan_amnt,
            "term_months": application.term,
            "interest_rate": application.int_rate,
            "emi_calculation": {
                "monthly_emi": emi_data.monthly_emi,
                "total_amount_payable": emi_data.total_amount_payable,
                "total_interest": emi_data.total_interest,
                "principal": emi_data.principal,
                "term_months": emi_data.term_months,
                "annual_interest_rate": emi_data.annual_interest_rate,
                "monthly_interest_rate": emi_data.monthly_interest_rate,
            },
            "financial_health": {
                "dti_ratio": health.dti_ratio,
                "dti_category": health.dti_category,
                "debt_to_income_percentage": health.debt_to_income_percentage,
                "loan_to_income_ratio": health.loan_to_income_ratio,
                "monthly_income": health.monthly_income,
                "monthly_emi": health.monthly_emi,
                "monthly_remaining_after_emi": health.monthly_remaining_after_emi,
                "emi_affordability": health.emi_affordability,
                "financial_health_score": health.financial_health_score,
            },
            "approval_probability": approval_score,
            "recommendations": recommendations,
            "prediction": prediction,
        }

    except Exception as e:
        logger.error(f"Error generating financial summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate financial summary",
        ) from e


# ============= ANALYTICS ENDPOINTS =============


@credit_router.get(
    "/analytics/metrics",
    summary="Get application metrics",
    description="Returns aggregated metrics for recent applications.",
)
async def get_analytics_metrics(hours: int = 24) -> dict:
    """Get analytics metrics for recent applications.

    Parameters
    ----------
    hours : int
        Number of hours to analyze (default: 24)

    Returns
    -------
    dict
        Aggregated metrics
    """
    try:
        from app.services.analytics import get_analytics_service
        
        service = get_analytics_service()
        metrics = service.get_metrics(hours=hours)

        return {
            "total_applications": metrics.total_applications,
            "total_approved": metrics.total_approved,
            "total_rejected": metrics.total_rejected,
            "approval_rate": metrics.approval_rate,
            "average_loan_amount": metrics.average_loan_amount,
            "average_fico_score": int(metrics.average_fico_score),
            "average_dti": metrics.average_dti,
            "average_interest_rate": metrics.average_interest_rate,
            "average_default_probability": metrics.average_default_probability,
            "average_approval_probability": metrics.average_approval_probability,
            "low_risk_count": metrics.low_risk_count,
            "medium_risk_count": metrics.medium_risk_count,
            "high_risk_count": metrics.high_risk_count,
        }

    except Exception as e:
        logger.error(f"Error getting analytics metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get metrics",
        ) from e


@credit_router.get(
    "/analytics/risk-distribution",
    summary="Get risk distribution",
    description="Returns the distribution of applications by risk level.",
)
async def get_risk_distribution(hours: int = 24) -> dict:
    """Get risk distribution for applications.

    Parameters
    ----------
    hours : int
        Number of hours to analyze

    Returns
    -------
    dict
        Risk distribution data
    """
    try:
        from app.services.analytics import get_analytics_service
        
        service = get_analytics_service()
        distribution = service.get_risk_distribution(hours=hours)

        return {
            "low_risk_percentage": distribution.low_risk_percentage,
            "medium_risk_percentage": distribution.medium_risk_percentage,
            "high_risk_percentage": distribution.high_risk_percentage,
            "low_risk_count": distribution.low_risk_count,
            "medium_risk_count": distribution.medium_risk_count,
            "high_risk_count": distribution.high_risk_count,
        }

    except Exception as e:
        logger.error(f"Error getting risk distribution: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get risk distribution",
        ) from e


@credit_router.get(
    "/analytics/recent-applications",
    summary="Get recent applications",
    description="Returns the most recent loan applications.",
)
async def get_recent_applications(limit: int = 10) -> dict:
    """Get recent applications.

    Parameters
    ----------
    limit : int
        Maximum number of applications to return

    Returns
    -------
    dict
        Recent applications data
    """
    try:
        from app.services.analytics import get_analytics_service
        
        service = get_analytics_service()
        applications = service.get_recent_applications(limit=limit)

        return {
            "applications": applications,
            "count": len(applications),
        }

    except Exception as e:
        logger.error(f"Error getting recent applications: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get recent applications",
        ) from e


@credit_router.get(
    "/analytics/approval-trend",
    summary="Get approval trend",
    description="Returns approval trend data over time.",
)
async def get_approval_trend(days: int = 7) -> dict:
    """Get approval trend.

    Parameters
    ----------
    days : int
        Number of days to analyze

    Returns
    -------
    dict
        Approval trend data
    """
    try:
        from app.services.analytics import get_analytics_service
        
        service = get_analytics_service()
        trend = service.get_approval_trend(days=days)

        return {
            "trend": trend,
            "days": days,
        }

    except Exception as e:
        logger.error(f"Error getting approval trend: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get approval trend",
        ) from e


@credit_router.get(
    "/analytics/dashboard-summary",
    summary="Get dashboard summary",
    description="Returns complete dashboard summary data.",
)
async def get_dashboard_summary() -> dict:
    """Get complete dashboard summary.

    Returns
    -------
    dict
        Complete dashboard data
    """
    try:
        from app.services.analytics import get_analytics_service
        
        service = get_analytics_service()
        summary = service.get_dashboard_summary()

        return summary

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get dashboard summary",
        ) from e
