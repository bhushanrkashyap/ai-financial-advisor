"""
Extended schemas for enhanced financial advisor features.
Includes financial breakdowns, analytics, and approval scoring.
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class EMICalculation(BaseModel):
    """Monthly EMI calculation details."""

    monthly_emi: float = Field(..., description="Monthly installment amount")
    total_amount_payable: float = Field(..., description="Total amount to be paid over the loan term")
    total_interest: float = Field(..., description="Total interest to be paid")
    principal: float = Field(..., description="Original loan principal")
    term_months: int = Field(..., description="Loan term in months")
    annual_interest_rate: float = Field(..., description="Annual interest rate (%)")
    monthly_interest_rate: float = Field(..., description="Monthly interest rate (%)")


class AmortizationMonth(BaseModel):
    """Single month amortization entry."""

    month: int = Field(..., description="Month number")
    principal_payment: float = Field(..., description="Principal paid in this month")
    interest_payment: float = Field(..., description="Interest paid in this month")
    remaining_balance: float = Field(..., description="Remaining loan balance")


class FinancialHealthIndicators(BaseModel):
    """Financial health metrics and indicators."""

    dti_ratio: float = Field(..., description="Debt-to-income ratio (0-1)")
    dti_category: str = Field(..., description="DTI category: EXCELLENT, GOOD, FAIR, POOR")
    debt_to_income_percentage: float = Field(..., description="DTI as percentage")
    loan_to_income_ratio: float = Field(..., description="Loan payment to income ratio (%)")
    monthly_income: float = Field(..., description="Monthly income")
    monthly_emi: float = Field(..., description="Monthly EMI payment")
    monthly_remaining_after_emi: float = Field(..., description="Monthly income after EMI")
    emi_affordability: str = Field(
        ..., description="Affordability category: HIGHLY_AFFORDABLE, AFFORDABLE, TIGHT, UNSUSTAINABLE"
    )
    financial_health_score: float = Field(..., ge=0, le=100, description="Financial health score (0-100)")


class ComponentScore(BaseModel):
    """Individual component score in approval calculation."""

    default_model_score: float = Field(..., description="ML model default risk score")
    dti_score: float = Field(..., description="DTI component score")
    fico_score: float = Field(..., description="FICO component score")
    employment_score: float = Field(..., description="Employment stability score")
    credit_history_score: float = Field(..., description="Credit history score")


class ApprovalProbability(BaseModel):
    """Comprehensive approval probability scoring."""

    approval_probability: float = Field(..., ge=0, le=100, description="Approval probability (0-100%)")
    approval_category: str = Field(
        ...,
        description="Category: HIGHLY_LIKELY, LIKELY, POSSIBLE, UNLIKELY, VERY_UNLIKELY",
    )
    composite_score: float = Field(..., ge=0, le=100, description="Composite approval score")
    component_scores: ComponentScore = Field(..., description="Individual component scores")


class Recommendation(BaseModel):
    """Single improvement recommendation."""

    category: str = Field(..., description="Recommendation category (e.g., CREDIT_SCORE, DTI, EMPLOYMENT)")
    priority: str = Field(..., description="Priority level: CRITICAL, HIGH, MEDIUM, LOW")
    recommendation: str = Field(..., description="Actionable recommendation text")
    potential_impact: str = Field(..., description="Potential improvement if action is taken")
    timeline: str = Field(..., description="Expected timeline for improvement")


class FinancialSummary(BaseModel):
    """Complete financial summary for a loan application."""

    loan_amount: float = Field(..., description="Requested loan amount")
    term_months: int = Field(..., description="Loan term in months")
    interest_rate: float = Field(..., description="Interest rate (%)")
    emi_calculation: EMICalculation = Field(..., description="EMI calculations")
    financial_health: FinancialHealthIndicators = Field(..., description="Financial health indicators")
    approval_probability: ApprovalProbability = Field(..., description="Approval probability scoring")
    recommendations: List[Recommendation] = Field(..., description="Improvement recommendations")


class EnhancedPredictionResponse(BaseModel):
    """Enhanced prediction response with all metrics."""

    prediction: str = Field(..., description="Prediction: 'SAFE' or 'DEFAULT_RISK'")
    default_probability: float = Field(..., ge=0, le=1, description="Probability of default")
    safe_probability: float = Field(..., ge=0, le=1, description="Probability of safe loan")
    risk_level: str = Field(..., description="Risk level: LOW_RISK, MEDIUM_RISK, HIGH_RISK")
    recommendation: str = Field(..., description="Recommendation text")
    confidence_score: float = Field(..., ge=0, le=1, description="Model confidence")
    approval_probability: float = Field(..., ge=0, le=100, description="Approval probability %")
    approval_category: str = Field(..., description="Approval likelihood category")
    emi_monthly: float = Field(..., description="Monthly EMI payment")
    total_interest: float = Field(..., description="Total interest over loan term")
    financial_health_score: float = Field(..., description="Financial health score")


class ApplicationMetricsResponse(BaseModel):
    """Application metrics response."""

    total_applications: int = Field(..., description="Total applications processed")
    total_approved: int = Field(..., description="Total approved applications")
    total_rejected: int = Field(..., description="Total rejected applications")
    approval_rate: float = Field(..., ge=0, le=1, description="Approval rate (0-1)")
    average_loan_amount: float = Field(..., description="Average loan amount")
    average_fico_score: float = Field(..., description="Average FICO score")
    average_dti: float = Field(..., description="Average DTI ratio")
    average_interest_rate: float = Field(..., description="Average interest rate")
    low_risk_count: int = Field(..., description="Count of low-risk applications")
    medium_risk_count: int = Field(..., description="Count of medium-risk applications")
    high_risk_count: int = Field(..., description="Count of high-risk applications")


class RiskDistributionResponse(BaseModel):
    """Risk distribution data."""

    low_risk_percentage: float = Field(..., description="Percentage of low-risk")
    medium_risk_percentage: float = Field(..., description="Percentage of medium-risk")
    high_risk_percentage: float = Field(..., description="Percentage of high-risk")
    low_risk_count: int = Field(..., description="Count of low-risk")
    medium_risk_count: int = Field(..., description="Count of medium-risk")
    high_risk_count: int = Field(..., description="Count of high-risk")


class RecentApplication(BaseModel):
    """Recent application record."""

    timestamp: str = Field(..., description="Application timestamp")
    loan_amount: str = Field(..., description="Formatted loan amount")
    fico_score: int = Field(..., description="FICO score")
    dti_ratio: str = Field(..., description="Formatted DTI ratio")
    interest_rate: str = Field(..., description="Formatted interest rate")
    risk_level: str = Field(..., description="Risk level")
    prediction: str = Field(..., description="Prediction result")
    approval_probability: str = Field(..., description="Formatted approval probability")


class ApprovalTrendDay(BaseModel):
    """Daily approval trend data."""

    date: str = Field(..., description="Date in ISO format")
    total: int = Field(..., description="Total applications")
    approved: int = Field(..., description="Approved applications")
    rejected: int = Field(..., description="Rejected applications")
    approval_rate: float = Field(..., description="Approval rate (%)")


class DashboardSummary(BaseModel):
    """Complete dashboard summary."""

    metrics_24h: dict = Field(..., description="24-hour metrics summary")
    metrics_7d: dict = Field(..., description="7-day metrics summary")
    risk_distribution: dict = Field(..., description="Risk distribution percentages")
    recent_applications: List[RecentApplication] = Field(..., description="Recent applications")
    approval_trend: List[ApprovalTrendDay] = Field(..., description="Approval trend data")
