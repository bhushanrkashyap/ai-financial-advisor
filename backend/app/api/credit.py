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
