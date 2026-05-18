"""
Financial calculations service for loan analysis.
Provides EMI, interest, amortization, and financial metrics calculations.
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class EMIBreakdown:
    """Detailed EMI calculation breakdown."""

    monthly_emi: float
    total_amount_payable: float
    total_interest: float
    principal: float
    term_months: int
    annual_interest_rate: float
    monthly_interest_rate: float
    approx_monthly_payment: float


@dataclass
class FinancialHealth:
    """Financial health metrics."""

    dti_ratio: float
    dti_category: str  # "EXCELLENT", "GOOD", "FAIR", "POOR"
    debt_to_income_percentage: float
    loan_to_income_ratio: float
    monthly_income: float
    monthly_emi: float
    monthly_remaining_after_emi: float
    emi_affordability: str  # "HIGHLY_AFFORDABLE", "AFFORDABLE", "TIGHT", "UNSUSTAINABLE"
    financial_health_score: float  # 0-100


@dataclass
class LoanAmortization:
    """Individual month amortization record."""

    month: int
    principal_payment: float
    interest_payment: float
    remaining_balance: float


class FinancialCalculator:
    """Service for financial calculations and analysis."""

    @staticmethod
    def calculate_emi(
        principal: float,
        annual_interest_rate: float,
        term_months: int,
    ) -> EMIBreakdown:
        """
        Calculate Equated Monthly Installment (EMI) using standard formula.

        EMI = P * [r(1+r)^n] / [(1+r)^n - 1]
        where:
        P = Principal amount (loan amount)
        r = Monthly interest rate (annual rate / 12 / 100)
        n = Number of months

        Parameters
        ----------
        principal : float
            Loan amount in USD
        annual_interest_rate : float
            Annual interest rate as percentage (e.g., 12.5 for 12.5%)
        term_months : int
            Loan term in months

        Returns
        -------
        EMIBreakdown
            Detailed EMI calculation breakdown
        """
        if principal <= 0:
            raise ValueError("Principal must be positive")
        if annual_interest_rate < 0:
            raise ValueError("Interest rate cannot be negative")
        if term_months <= 0:
            raise ValueError("Term must be positive")

        # Convert annual rate to monthly decimal
        monthly_rate = annual_interest_rate / 12 / 100

        # Handle zero interest rate
        if monthly_rate == 0:
            monthly_emi = principal / term_months
            total_amount_payable = principal
            total_interest = 0
        else:
            # EMI formula
            numerator = monthly_rate * ((1 + monthly_rate) ** term_months)
            denominator = ((1 + monthly_rate) ** term_months) - 1
            monthly_emi = principal * (numerator / denominator)

            total_amount_payable = monthly_emi * term_months
            total_interest = total_amount_payable - principal

        return EMIBreakdown(
            monthly_emi=round(monthly_emi, 2),
            total_amount_payable=round(total_amount_payable, 2),
            total_interest=round(total_interest, 2),
            principal=round(principal, 2),
            term_months=term_months,
            annual_interest_rate=annual_interest_rate,
            monthly_interest_rate=round(monthly_rate * 100, 4),
            approx_monthly_payment=round(monthly_emi, 2),
        )

    @staticmethod
    def generate_amortization_schedule(
        principal: float,
        annual_interest_rate: float,
        term_months: int,
        include_all_months: bool = False,
    ) -> list[LoanAmortization]:
        """
        Generate complete amortization schedule.

        Parameters
        ----------
        principal : float
            Loan amount in USD
        annual_interest_rate : float
            Annual interest rate as percentage
        term_months : int
            Loan term in months
        include_all_months : bool
            If True, include all months; if False, include first 3, last 3, and sample

        Returns
        -------
        list[LoanAmortization]
            List of amortization records for each month
        """
        emi_data = FinancialCalculator.calculate_emi(
            principal, annual_interest_rate, term_months
        )

        monthly_rate = emi_data.monthly_interest_rate / 100
        schedule = []
        remaining_balance = principal

        for month in range(1, term_months + 1):
            interest_payment = remaining_balance * monthly_rate
            principal_payment = emi_data.monthly_emi - interest_payment
            remaining_balance -= principal_payment

            # Ensure no negative balance due to rounding
            remaining_balance = max(0, remaining_balance)

            schedule.append(
                LoanAmortization(
                    month=month,
                    principal_payment=round(principal_payment, 2),
                    interest_payment=round(interest_payment, 2),
                    remaining_balance=round(remaining_balance, 2),
                )
            )

        # Return sample if requested
        if not include_all_months and term_months > 6:
            return schedule[:3] + schedule[-3:]

        return schedule

    @staticmethod
    def calculate_financial_health(
        annual_income: float,
        monthly_emi: float,
        existing_debt_emi: float = 0,
        employment_years: int = 0,
        delinquencies: int = 0,
    ) -> FinancialHealth:
        """
        Calculate comprehensive financial health metrics.

        Parameters
        ----------
        annual_income : float
            Annual income in USD
        monthly_emi : float
            New loan EMI monthly payment
        existing_debt_emi : float
            Existing monthly debt obligations
        employment_years : int
            Years of employment
        delinquencies : int
            Number of delinquencies in last 2 years

        Returns
        -------
        FinancialHealth
            Financial health assessment
        """
        if annual_income <= 0:
            raise ValueError("Annual income must be positive")

        monthly_income = annual_income / 12
        total_monthly_debt = monthly_emi + existing_debt_emi
        dti_ratio = total_monthly_debt / monthly_income

        # Categorize DTI ratio
        if dti_ratio <= 0.36:
            dti_category = "EXCELLENT"
        elif dti_ratio <= 0.43:
            dti_category = "GOOD"
        elif dti_ratio <= 0.50:
            dti_category = "FAIR"
        else:
            dti_category = "POOR"

        # Monthly remaining after EMI
        monthly_remaining = monthly_income - total_monthly_debt

        # EMI affordability
        if monthly_remaining >= monthly_income * 0.4:
            emi_affordability = "HIGHLY_AFFORDABLE"
        elif monthly_remaining >= monthly_income * 0.25:
            emi_affordability = "AFFORDABLE"
        elif monthly_remaining >= monthly_income * 0.10:
            emi_affordability = "TIGHT"
        else:
            emi_affordability = "UNSUSTAINABLE"

        # Financial health score (0-100)
        score = 100.0

        # DTI impact (40 points)
        dti_score = max(0, 40 - (dti_ratio * 80))
        score -= 40 - dti_score

        # Employment stability (20 points)
        if employment_years >= 5:
            employment_score = 20
        elif employment_years >= 2:
            employment_score = 15
        elif employment_years >= 1:
            employment_score = 10
        else:
            employment_score = 5
        score -= 20 - employment_score

        # Credit history (40 points)
        if delinquencies == 0:
            delinq_score = 40
        elif delinquencies == 1:
            delinq_score = 30
        elif delinquencies <= 3:
            delinq_score = 15
        else:
            delinq_score = 5
        score -= 40 - delinq_score

        score = max(0, min(100, score))

        return FinancialHealth(
            dti_ratio=round(dti_ratio, 4),
            dti_category=dti_category,
            debt_to_income_percentage=round(dti_ratio * 100, 2),
            loan_to_income_ratio=round((monthly_emi / monthly_income) * 100, 2),
            monthly_income=round(monthly_income, 2),
            monthly_emi=round(monthly_emi, 2),
            monthly_remaining_after_emi=round(monthly_remaining, 2),
            emi_affordability=emi_affordability,
            financial_health_score=round(score, 2),
        )

    @staticmethod
    def calculate_approval_probability_score(
        default_probability: float,
        dti_ratio: float,
        fico_score: int,
        employment_years: int,
        delinquencies: int,
    ) -> dict:
        """
        Calculate composite approval probability score.

        Parameters
        ----------
        default_probability : float
            Model-predicted default probability (0-1)
        dti_ratio : float
            Debt-to-income ratio (0-1)
        fico_score : int
            FICO credit score (300-850)
        employment_years : int
            Years of employment
        delinquencies : int
            Delinquencies in last 2 years

        Returns
        -------
        dict
            Approval score and breakdown
        """
        score = 100.0

        # Model default probability (40% weight)
        # Invert so lower default prob = higher score
        default_score = (1 - default_probability) * 100
        score_from_default = default_score * 0.40

        # DTI component (25% weight)
        if dti_ratio <= 0.36:
            dti_score = 100
        elif dti_ratio <= 0.43:
            dti_score = 85
        elif dti_ratio <= 0.50:
            dti_score = 70
        else:
            dti_score = max(0, 100 - (dti_ratio * 200))
        score_from_dti = dti_score * 0.25

        # FICO component (20% weight)
        if fico_score >= 750:
            fico_norm = 100
        elif fico_score >= 700:
            fico_norm = 90
        elif fico_score >= 650:
            fico_norm = 75
        elif fico_score >= 600:
            fico_norm = 60
        else:
            fico_norm = max(0, (fico_score - 300) / 3)
        score_from_fico = fico_norm * 0.20

        # Employment stability (10% weight)
        if employment_years >= 5:
            emp_score = 100
        elif employment_years >= 2:
            emp_score = 80
        elif employment_years >= 1:
            emp_score = 60
        else:
            emp_score = 40
        score_from_emp = emp_score * 0.10

        # Credit history / delinquencies (5% weight)
        if delinquencies == 0:
            delinq_score = 100
        elif delinquencies == 1:
            delinq_score = 80
        elif delinquencies <= 3:
            delinq_score = 50
        else:
            delinq_score = 20
        score_from_delinq = delinq_score * 0.05

        # Composite score
        composite_score = (
            score_from_default + score_from_dti + score_from_fico + score_from_emp + score_from_delinq
        )
        composite_score = min(100, max(0, composite_score))

        # Approval probability (0-100%)
        approval_prob = composite_score

        # Categorize
        if approval_prob >= 80:
            approval_category = "HIGHLY_LIKELY"
        elif approval_prob >= 65:
            approval_category = "LIKELY"
        elif approval_prob >= 50:
            approval_category = "POSSIBLE"
        elif approval_prob >= 35:
            approval_category = "UNLIKELY"
        else:
            approval_category = "VERY_UNLIKELY"

        return {
            "approval_probability": round(approval_prob, 2),
            "approval_category": approval_category,
            "composite_score": round(composite_score, 2),
            "component_scores": {
                "default_model_score": round(score_from_default, 2),
                "dti_score": round(score_from_dti, 2),
                "fico_score": round(score_from_fico, 2),
                "employment_score": round(score_from_emp, 2),
                "credit_history_score": round(score_from_delinq, 2),
            },
        }

    @staticmethod
    def calculate_improvement_recommendations(
        fico_score: int,
        dti_ratio: float,
        delinquencies: int,
        employment_years: int,
        default_probability: float,
    ) -> list[dict]:
        """
        Generate actionable improvement recommendations.

        Parameters
        ----------
        fico_score : int
            Current FICO score
        dti_ratio : float
            Current DTI ratio
        delinquencies : int
            Current delinquencies
        employment_years : int
            Years of employment
        default_probability : float
            Model-predicted default probability

        Returns
        -------
        list[dict]
            List of recommendations with priority and potential impact
        """
        recommendations = []

        # FICO Score Recommendations
        if fico_score < 600:
            recommendations.append(
                {
                    "category": "CREDIT_SCORE",
                    "priority": "CRITICAL",
                    "recommendation": "Your FICO score is below 600. Focus on paying bills on time and reducing outstanding balances.",
                    "potential_impact": "Increasing FICO by 50 points could improve approval odds by 15-20%",
                    "timeline": "6-12 months",
                }
            )
        elif fico_score < 650:
            recommendations.append(
                {
                    "category": "CREDIT_SCORE",
                    "priority": "HIGH",
                    "recommendation": "Your FICO score is fair. Continue building positive payment history.",
                    "potential_impact": "Increasing FICO by 30 points could improve approval odds by 8-12%",
                    "timeline": "3-6 months",
                }
            )
        elif fico_score < 700:
            recommendations.append(
                {
                    "category": "CREDIT_SCORE",
                    "priority": "MEDIUM",
                    "recommendation": "Your FICO score is good. Minor improvements could help.",
                    "potential_impact": "Increasing FICO by 20 points could improve approval odds by 3-5%",
                    "timeline": "2-3 months",
                }
            )

        # DTI Recommendations
        if dti_ratio > 0.50:
            recommendations.append(
                {
                    "category": "DEBT_TO_INCOME",
                    "priority": "CRITICAL",
                    "recommendation": f"Your DTI ratio is {dti_ratio*100:.1f}%, which is very high. Consider paying down existing debts or increasing income.",
                    "potential_impact": "Reducing DTI to below 0.43 could improve approval odds by 20-30%",
                    "timeline": "Ongoing",
                }
            )
        elif dti_ratio > 0.43:
            recommendations.append(
                {
                    "category": "DEBT_TO_INCOME",
                    "priority": "HIGH",
                    "recommendation": f"Your DTI ratio is {dti_ratio*100:.1f}%. Consider paying down some existing debts.",
                    "potential_impact": "Reducing DTI to below 0.36 could improve approval odds by 10-15%",
                    "timeline": "6 months",
                }
            )

        # Delinquency Recommendations
        if delinquencies > 0:
            recommendations.append(
                {
                    "category": "PAYMENT_HISTORY",
                    "priority": "CRITICAL",
                    "recommendation": f"You have {delinquencies} delinquency/delinquencies. Focus on maintaining perfect payment records going forward.",
                    "potential_impact": "Eliminating delinquencies over time could improve approval odds by 15-25%",
                    "timeline": "2 years (delinquencies age off credit report)",
                }
            )

        # Employment Stability Recommendations
        if employment_years < 1:
            recommendations.append(
                {
                    "category": "EMPLOYMENT",
                    "priority": "MEDIUM",
                    "recommendation": "Your employment history is recent. Staying with current employer can strengthen future applications.",
                    "potential_impact": "6 months of employment stability could improve approval odds by 5-10%",
                    "timeline": "6 months",
                }
            )
        elif employment_years < 2:
            recommendations.append(
                {
                    "category": "EMPLOYMENT",
                    "priority": "LOW",
                    "recommendation": "Continue building employment stability with your current employer.",
                    "potential_impact": "2 years of employment could improve approval odds by 3-5%",
                    "timeline": "1 year",
                }
            )

        # Overall Risk Recommendations
        if default_probability > 0.6:
            recommendations.append(
                {
                    "category": "OVERALL_RISK",
                    "priority": "CRITICAL",
                    "recommendation": "Your application presents elevated risk. Consider reapplying in 3-6 months after addressing the above areas.",
                    "potential_impact": "Addressing multiple factors could significantly improve approval odds",
                    "timeline": "3-6 months",
                }
            )
        elif default_probability > 0.4:
            recommendations.append(
                {
                    "category": "OVERALL_RISK",
                    "priority": "HIGH",
                    "recommendation": "Your application is borderline. Addressing the recommendations above could help.",
                    "potential_impact": "Targeted improvements could improve approval odds by 15-25%",
                    "timeline": "1-3 months",
                }
            )

        return recommendations


# Singleton instance getter
_calculator_instance: Optional[FinancialCalculator] = None


def get_financial_calculator() -> FinancialCalculator:
    """Get or create financial calculator singleton."""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = FinancialCalculator()
    return _calculator_instance
