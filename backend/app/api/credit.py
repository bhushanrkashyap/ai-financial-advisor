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
from app.services.house_price_service import HousePriceService
from app.services.market_risk_service import MarketRiskService

logger = logging.getLogger(__name__)

credit_router = APIRouter(prefix="/credit", tags=["credit"])

# Initialize services
house_price_service = HousePriceService()
market_risk_service = MarketRiskService()


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


# ============= HOUSE PRICE PREDICTION ENDPOINTS =============


@credit_router.post(
    "/collateral/estimate-house-price",
    summary="Estimate house price for collateral valuation",
    description="Predicts residential property price using house features.",
)
async def estimate_house_price(house_features: dict) -> dict:
    """Estimate house price for collateral valuation.

    Parameters
    ----------
    house_features : dict
        House features including:
        - total_sqft: Total square feet
        - bhk: Number of bedrooms
        - bath: Number of bathrooms
        - balcony: Number of balconies
        - area_type_encoded: Encoded area type
        - availability_encoded: Encoded availability
        - location_encoded: Encoded location
        - has_society: Whether property is in a society

    Returns
    -------
    dict
        House price prediction with confidence and uncertainty estimates
    """
    try:
        if not house_price_service.is_loaded:
            # Fallback: simple heuristic estimate using sqft * price_per_sqft when available
            sqft = float(house_features.get("total_sqft", 0))
            ppsq = float(house_features.get("price_per_sqft", 0))
            if sqft > 0 and ppsq > 0:
                est = sqft * ppsq
            else:
                # conservative default if inputs missing
                est = 1500 * 45000

            fallback = {
                "predicted_price": est,
                "confidence": 0.4,
                "uncertainty": 0.25,
                "uncertainty_range": {"lower": est * 0.75, "upper": est * 1.25},
                "model_used": "heuristic_fallback",
            }
            return fallback

        result = house_price_service.predict_price(house_features, model_name='xgboost')

        if result.get('status') == 'error':
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Prediction failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"House price estimation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"House price estimation failed: {str(e)}",
        ) from e


@credit_router.get(
    "/collateral/estimate-house-price",
    summary="Estimate house price (GET)",
    description="Estimate house price using query params (fallback for GET clients)",
)
async def estimate_house_price_get(
    total_sqft: float | None = None,
    price_per_sqft: float | None = None,
    bhk: int | None = None,
    bath: int | None = None,
    balcony: int | None = None,
    area_type_encoded: int | None = None,
    availability_encoded: int | None = None,
    location_encoded: int | None = None,
    has_society: int | None = None,
) -> dict:
    """Wrapper to accept GET requests and forward to POST handler"""
    house_features = {}
    if total_sqft is not None:
        house_features["total_sqft"] = total_sqft
    if price_per_sqft is not None:
        house_features["price_per_sqft"] = price_per_sqft
    if bhk is not None:
        house_features["bhk"] = bhk
    if bath is not None:
        house_features["bath"] = bath
    if balcony is not None:
        house_features["balcony"] = balcony
    if area_type_encoded is not None:
        house_features["area_type_encoded"] = area_type_encoded
    if availability_encoded is not None:
        house_features["availability_encoded"] = availability_encoded
    if location_encoded is not None:
        house_features["location_encoded"] = location_encoded
    if has_society is not None:
        house_features["has_society"] = has_society

    return await estimate_house_price(house_features)


@credit_router.post(
    "/collateral/ensemble-estimate",
    summary="Ensemble house price estimation",
    description="Predicts house price using ensemble of multiple models.",
)
async def ensemble_house_price_estimate(house_features: dict) -> dict:
    """Ensemble house price estimation using multiple models.

    Parameters
    ----------
    house_features : dict
        House features

    Returns
    -------
    dict
        Ensemble prediction with individual model predictions and consensus score
    """
    try:
        if not house_price_service.is_loaded:
            # Fallback ensemble: produce simple ensemble from heuristic + saved models if available
            sqft = float(house_features.get("total_sqft", 0))
            ppsq = float(house_features.get("price_per_sqft", 0))
            if sqft > 0 and ppsq > 0:
                base = sqft * ppsq
            else:
                base = 1500 * 45000

            indiv = {
                "xgboost": base * 1.0,
                "random_forest": base * 0.98,
                "linear_regression": base * 1.02,
            }
            ensemble = {
                "ensemble_price": sum(indiv.values()) / len(indiv),
                "individual_predictions": indiv,
                "consensus_score": 0.6,
                "std_deviation": (max(indiv.values()) - min(indiv.values())) / 2,
                "predicted_price": sum(indiv.values()) / len(indiv),
                "confidence": 0.45,
                "uncertainty": 0.25,
                "uncertainty_range": {"lower": base * 0.75, "upper": base * 1.25},
                "model_used": "heuristic_ensemble_fallback",
            }
            return ensemble

        result = house_price_service.predict_ensemble(house_features)

        if result.get('status') == 'error':
            raise HTTPException(
                status_code=400,
                detail=result.get('message', 'Prediction failed')
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ensemble estimation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ensemble estimation failed: {str(e)}",
        ) from e


@credit_router.get(
    "/collateral/ensemble-estimate",
    summary="Ensemble house price estimate (GET)",
    description="Ensemble estimate via query params (fallback for GET clients)",
)
async def ensemble_house_price_estimate_get(
    total_sqft: float | None = None,
    price_per_sqft: float | None = None,
    bhk: int | None = None,
    bath: int | None = None,
    balcony: int | None = None,
    area_type_encoded: int | None = None,
    availability_encoded: int | None = None,
    location_encoded: int | None = None,
    has_society: int | None = None,
) -> dict:
    features = {}
    if total_sqft is not None:
        features["total_sqft"] = total_sqft
    if price_per_sqft is not None:
        features["price_per_sqft"] = price_per_sqft
    if bhk is not None:
        features["bhk"] = bhk
    if bath is not None:
        features["bath"] = bath
    if balcony is not None:
        features["balcony"] = balcony
    if area_type_encoded is not None:
        features["area_type_encoded"] = area_type_encoded
    if availability_encoded is not None:
        features["availability_encoded"] = availability_encoded
    if location_encoded is not None:
        features["location_encoded"] = location_encoded
    if has_society is not None:
        features["has_society"] = has_society

    return await ensemble_house_price_estimate(features)


@credit_router.get(
    "/collateral/health",
    summary="Health check for house price service",
    description="Checks if the house price prediction service is ready.",
)
async def house_price_health_check() -> dict:
    """Health check for house price service.

    Returns
    -------
    dict
        Health status and model availability
    """
    return house_price_service.health_check()


# ============= MARKET RISK & PORTFOLIO ENDPOINTS =============


@credit_router.get(
    "/market/conditions",
    summary="Get current market conditions",
    description="Returns current market conditions, volatility, and risk indicators.",
)
async def get_market_conditions() -> dict:
    """Get current market conditions and risk indicators.

    Returns
    -------
    dict
        Market conditions with volatility, trend, VIX equivalent, and stress index
    """
    try:
        if not market_risk_service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Market data not available.",
            )

        conditions = market_risk_service.get_current_market_conditions()

        if conditions.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=conditions.get('message', 'Failed to get market conditions')
            )

        return conditions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting market conditions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get market conditions",
        ) from e


@credit_router.get(
    "/market/sector-analysis",
    summary="Get sector and stock analysis",
    description="Returns sector/stock volatility and performance metrics.",
)
async def get_sector_analysis() -> dict:
    """Get sector and stock analysis.

    Returns
    -------
    dict
        Sector volatility, performance, and market health score
    """
    try:
        if not market_risk_service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Sector data not available.",
            )

        analysis = market_risk_service.get_sector_analysis()

        if analysis.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=analysis.get('message', 'Failed to get sector analysis')
            )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sector analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get sector analysis",
        ) from e


@credit_router.post(
    "/portfolio/recommend",
    summary="Get portfolio recommendation",
    description="Recommends personalized portfolio allocation based on risk profile and income.",
)
async def recommend_portfolio(risk_level: str = "moderate", income: float = 500000) -> dict:
    """Get personalized portfolio recommendation.

    Parameters
    ----------
    risk_level : str
        Risk level: 'conservative', 'moderate', or 'aggressive'
    income : float
        Annual income in INR

    Returns
    -------
    dict
        Portfolio allocation, investment amounts, and expected returns
    """
    try:
        # Validate inputs
        if risk_level not in ['conservative', 'moderate', 'aggressive']:
            raise HTTPException(
                status_code=400,
                detail="Risk level must be 'conservative', 'moderate', or 'aggressive'"
            )

        if income <= 0:
            raise HTTPException(
                status_code=400,
                detail="Income must be positive"
            )

        if not market_risk_service.is_loaded:
            # Fallback portfolio recommendation (simple heuristics)
            monthly = income / 12
            base_alloc = {
                'conservative': {'stocks': 0.3, 'bonds': 0.5, 'gold': 0.1, 'cash': 0.1},
                'moderate': {'stocks': 0.5, 'bonds': 0.3, 'gold': 0.1, 'cash': 0.1},
                'aggressive': {'stocks': 0.7, 'bonds': 0.15, 'gold': 0.1, 'cash': 0.05},
            }
            alloc = base_alloc.get(risk_level, base_alloc['moderate'])
            allocation_decimal = {k: v for (k, v) in alloc.items()}
            allocation = {k: round(v, 2) for (k, v) in alloc.items()}
            monthly_investment = round(monthly * 0.2)  # suggest 20% of monthly income
            annual_investment = monthly_investment * 12
            expected_annual_return = 0.06 if risk_level == 'conservative' else 0.08 if risk_level == 'moderate' else 0.10
            volatility = 0.06 if risk_level == 'conservative' else 0.12 if risk_level == 'moderate' else 0.2
            sharpe_ratio = expected_annual_return / (volatility + 1e-6)

            return {
                'allocation': allocation,
                'allocation_decimal': allocation_decimal,
                'monthly_investment': monthly_investment,
                'annual_investment': annual_investment,
                'expected_annual_return': expected_annual_return,
                'volatility': volatility,
                'sharpe_ratio': round(sharpe_ratio, 2),
                'notes': 'Fallback heuristic portfolio recommendation. Run market data services for improved results.'
            }

        recommendation = market_risk_service.recommend_portfolio(risk_level, income)

        if recommendation.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=recommendation.get('message', 'Failed to generate recommendation')
            )

        return recommendation

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recommending portfolio: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to recommend portfolio",
        ) from e


@credit_router.get(
    "/portfolio/recommend",
    summary="Get portfolio recommendation (GET)",
    description="Wrapper to allow GET requests for portfolio recommendations",
)
async def recommend_portfolio_get(risk_level: str = "moderate", income: float = 500000) -> dict:
    return await recommend_portfolio(risk_level=risk_level, income=income)


@credit_router.post(
    "/market/loan-default-risk",
    summary="Analyze market-adjusted loan default risk",
    description="Analyzes loan default risk adjusted for current market conditions.",
)
async def analyze_loan_market_risk(market_conditions: dict = None, borrower_income: float = 500000) -> dict:
    """Analyze loan default risk considering market conditions.

    Parameters
    ----------
    market_conditions : dict, optional
        Current market conditions. If None, uses latest market data.
    borrower_income : float
        Borrower's annual income in INR

    Returns
    -------
    dict
        Market-adjusted risk score and recommendations
    """
    try:
        if not market_risk_service.is_loaded:
            raise HTTPException(
                status_code=503,
                detail="Market data not available.",
            )

        # Get current market conditions if not provided
        if market_conditions is None:
            market_conditions = market_risk_service.get_current_market_conditions()
            if market_conditions.get('status') == 'error':
                raise HTTPException(
                    status_code=500,
                    detail="Failed to get market conditions"
                )

        risk_analysis = market_risk_service.analyze_loan_default_risk(
            market_conditions, borrower_income
        )

        if risk_analysis.get('status') == 'error':
            raise HTTPException(
                status_code=500,
                detail=risk_analysis.get('message', 'Failed to analyze risk')
            )

        return risk_analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing loan market risk: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze loan market risk",
        ) from e


@credit_router.get(
    "/market/health",
    summary="Health check for market service",
    description="Checks if the market risk analysis service is ready.",
)
async def market_risk_health_check() -> dict:
    """Health check for market risk service.

    Returns
    -------
    dict
        Health status and data availability
    """
    return market_risk_service.health_check()
