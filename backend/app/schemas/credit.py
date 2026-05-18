"""
Schemas for credit default prediction requests and responses.
"""

from pydantic import BaseModel, ConfigDict, Field


class LoanApplicationInput(BaseModel):
    """Input schema for credit default prediction."""

    loan_amnt: float = Field(..., ge=50000, le=500000000, description="Loan amount in INR")
    term: int = Field(..., description="Loan term in months (36 or 60)")
    int_rate: float = Field(..., ge=0, le=30, description="Interest rate (annual %)")
    installment: float = Field(..., ge=0, description="Monthly installment amount in INR")
    emp_length: int = Field(..., ge=0, le=70, description="Years of employment")
    annual_inc: float = Field(..., ge=200000, description="Annual income in INR")
    dti: float = Field(..., ge=0, le=1, description="Debt-to-income ratio (0-1)")
    delinq_2yrs: int = Field(default=0, ge=0, description="Delinquencies in last 2 years")
    inq_last_6mths: int = Field(default=0, ge=0, description="Inquiries in last 6 months")
    open_acc: int = Field(default=5, ge=0, description="Number of open accounts")
    pub_rec: int = Field(default=0, ge=0, description="Number of public records")
    revol_bal: float = Field(default=0, ge=0, description="Revolving balance in INR")
    revol_util: float = Field(default=0.3, ge=0, le=1, description="Revolving utilization ratio")
    fico_avg: int = Field(..., ge=300, le=850, description="Average FICO score")
    grade_encoded: int = Field(..., ge=1, le=7, description="Loan grade (1-7)")
    sub_grade_encoded: int = Field(..., ge=1, le=35, description="Loan sub-grade (1-35)")
    home_ownership_MORTGAGE: int = Field(default=0, description="Home owned via mortgage")
    home_ownership_OWN: int = Field(default=0, description="Home owned outright")
    home_ownership_RENT: int = Field(default=1, description="Home rented")
    verification_status_Verified: int = Field(default=1, description="Income verified")
    verification_status_Source_Verified: int = Field(
        default=0,
        description="Source verified",
        alias="verification_status_Source Verified",
    )
    purpose_credit_card: int = Field(default=0, description="Loan purpose is credit card payoff")
    purpose_debt_consolidation: int = Field(
        default=1, description="Loan purpose is debt consolidation"
    )
    purpose_car: int = Field(default=0, description="Loan purpose is car purchase")
    purpose_medical: int = Field(default=0, description="Loan purpose is medical")
    purpose_home_improvement: int = Field(default=0, description="Loan purpose is home improvement")
    application_type_Individual: int = Field(default=1, description="Individual application")
    application_type_Joint_App: int = Field(
        default=0,
        description="Joint application",
        alias="application_type_Joint App",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "loan_amnt": 500000,
                "term": 60,
                "int_rate": 12.5,
                "installment": 10000,
                "emp_length": 5,
                "annual_inc": 750000,
                "dti": 0.25,
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
            }
        },
    )


class CreditPredictionResponse(BaseModel):
    """Response schema for credit prediction."""

    prediction: str = Field(..., description="Prediction: 'SAFE' or 'DEFAULT_RISK'")
    default_probability: float = Field(
        ..., ge=0, le=1, description="Probability of default (0-1)"
    )
    safe_probability: float = Field(
        ..., ge=0, le=1, description="Probability of safe loan (0-1)"
    )
    risk_level: str = Field(
        ..., description="Risk assessment: 'LOW_RISK', 'MEDIUM_RISK', or 'HIGH_RISK'"
    )
    recommendation: str = Field(..., description="Recommendation based on risk")
    confidence_score: float = Field(
        ..., ge=0, le=1, description="Model confidence in prediction"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    version: str
