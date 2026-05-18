"""
Analytics service for tracking loan applications and generating insights.
Provides aggregated data for dashboard visualization and trend analysis.
"""

from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
import json
from pathlib import Path


@dataclass
class ApplicationMetrics:
    """Aggregated application metrics."""

    total_applications: int
    total_approved: int
    total_rejected: int
    approval_rate: float
    average_loan_amount: float
    average_fico_score: float
    average_dti: float
    average_interest_rate: float
    average_default_probability: float
    average_approval_probability: float
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class RiskDistribution:
    """Risk level distribution."""

    low_risk_percentage: float
    medium_risk_percentage: float
    high_risk_percentage: float
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int


@dataclass
class ApplicationRecord:
    """Single application record for analytics."""

    timestamp: str
    loan_amount: float
    fico_score: int
    dti_ratio: float
    interest_rate: float
    default_probability: float
    approval_probability: float
    risk_level: str
    prediction: str
    approved: Optional[bool] = None


class AnalyticsService:
    """Service for application analytics and insights."""

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize analytics service.

        Parameters
        ----------
        data_file : Path, optional
            Path to JSON file storing application records. If None, uses default.
        """
        if data_file is None:
            # Use backend/app/data/applications.json
            current_dir = Path(__file__).resolve().parent.parent
            data_file = current_dir / "data" / "applications.json"

        self.data_file = data_file
        self.records: list[ApplicationRecord] = []
        self._load_records()

    def _load_records(self) -> None:
        """Load records from JSON file."""
        try:
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.records = [ApplicationRecord(**record) for record in data]
            else:
                self.records = []
        except Exception as e:
            print(f"Failed to load analytics records: {e}")
            self.records = []

    def _save_records(self) -> None:
        """Save records to JSON file."""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w") as f:
                data = [
                    {
                        "timestamp": r.timestamp,
                        "loan_amount": r.loan_amount,
                        "fico_score": r.fico_score,
                        "dti_ratio": r.dti_ratio,
                        "interest_rate": r.interest_rate,
                        "default_probability": r.default_probability,
                        "approval_probability": r.approval_probability,
                        "risk_level": r.risk_level,
                        "prediction": r.prediction,
                        "approved": r.approved,
                    }
                    for r in self.records
                ]
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save analytics records: {e}")

    def record_application(
        self,
        loan_amount: float,
        fico_score: int,
        dti_ratio: float,
        interest_rate: float,
        default_probability: float,
        approval_probability: float,
        risk_level: str,
        prediction: str,
        approved: Optional[bool] = None,
    ) -> None:
        """
        Record a new application.

        Parameters
        ----------
        loan_amount : float
            Loan amount requested
        fico_score : int
            FICO score
        dti_ratio : float
            Debt-to-income ratio
        interest_rate : float
            Interest rate
        default_probability : float
            Probability of default
        approval_probability : float
            Approval probability score
        risk_level : str
            Risk level classification
        prediction : str
            Prediction result
        approved : bool, optional
            Whether application was approved
        """
        record = ApplicationRecord(
            timestamp=datetime.now().isoformat(),
            loan_amount=loan_amount,
            fico_score=fico_score,
            dti_ratio=dti_ratio,
            interest_rate=interest_rate,
            default_probability=default_probability,
            approval_probability=approval_probability,
            risk_level=risk_level,
            prediction=prediction,
            approved=approved,
        )
        self.records.append(record)
        self._save_records()

    def get_metrics(self, hours: int = 24) -> ApplicationMetrics:
        """
        Get aggregated metrics for recent applications.

        Parameters
        ----------
        hours : int
            Number of hours to look back (default: last 24 hours)

        Returns
        -------
        ApplicationMetrics
            Aggregated metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_records = [
            r for r in self.records if datetime.fromisoformat(r.timestamp) > cutoff_time
        ]

        if not filtered_records:
            return ApplicationMetrics(
                total_applications=0,
                total_approved=0,
                total_rejected=0,
                approval_rate=0.0,
                average_loan_amount=0.0,
                average_fico_score=0.0,
                average_dti=0.0,
                average_interest_rate=0.0,
                average_default_probability=0.0,
                average_approval_probability=0.0,
                low_risk_count=0,
                medium_risk_count=0,
                high_risk_count=0,
            )

        total_approved = sum(1 for r in filtered_records if r.prediction == "SAFE")
        total_rejected = sum(1 for r in filtered_records if r.prediction == "DEFAULT_RISK")

        low_risk = sum(1 for r in filtered_records if r.risk_level == "LOW_RISK")
        medium_risk = sum(1 for r in filtered_records if r.risk_level == "MEDIUM_RISK")
        high_risk = sum(1 for r in filtered_records if r.risk_level == "HIGH_RISK")

        return ApplicationMetrics(
            total_applications=len(filtered_records),
            total_approved=total_approved,
            total_rejected=total_rejected,
            approval_rate=round(total_approved / len(filtered_records), 4)
            if filtered_records
            else 0.0,
            average_loan_amount=round(
                sum(r.loan_amount for r in filtered_records) / len(filtered_records), 2
            ),
            average_fico_score=round(
                sum(r.fico_score for r in filtered_records) / len(filtered_records), 0
            ),
            average_dti=round(
                sum(r.dti_ratio for r in filtered_records) / len(filtered_records), 4
            ),
            average_interest_rate=round(
                sum(r.interest_rate for r in filtered_records) / len(filtered_records), 2
            ),
            average_default_probability=round(
                sum(r.default_probability for r in filtered_records) / len(filtered_records), 4
            ),
            average_approval_probability=round(
                sum(r.approval_probability for r in filtered_records) / len(filtered_records), 2
            ),
            low_risk_count=low_risk,
            medium_risk_count=medium_risk,
            high_risk_count=high_risk,
        )

    def get_risk_distribution(self, hours: int = 24) -> RiskDistribution:
        """
        Get risk level distribution.

        Parameters
        ----------
        hours : int
            Number of hours to look back

        Returns
        -------
        RiskDistribution
            Risk distribution percentages
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_records = [
            r for r in self.records if datetime.fromisoformat(r.timestamp) > cutoff_time
        ]

        if not filtered_records:
            return RiskDistribution(
                low_risk_percentage=0.0,
                medium_risk_percentage=0.0,
                high_risk_percentage=0.0,
                low_risk_count=0,
                medium_risk_count=0,
                high_risk_count=0,
            )

        low_risk = sum(1 for r in filtered_records if r.risk_level == "LOW_RISK")
        medium_risk = sum(1 for r in filtered_records if r.risk_level == "MEDIUM_RISK")
        high_risk = sum(1 for r in filtered_records if r.risk_level == "HIGH_RISK")

        total = len(filtered_records)

        return RiskDistribution(
            low_risk_percentage=round((low_risk / total) * 100, 2) if total > 0 else 0.0,
            medium_risk_percentage=round((medium_risk / total) * 100, 2) if total > 0 else 0.0,
            high_risk_percentage=round((high_risk / total) * 100, 2) if total > 0 else 0.0,
            low_risk_count=low_risk,
            medium_risk_count=medium_risk,
            high_risk_count=high_risk,
        )

    def get_recent_applications(self, limit: int = 10) -> list[dict]:
        """
        Get most recent applications.

        Parameters
        ----------
        limit : int
            Maximum number of applications to return

        Returns
        -------
        list[dict]
            Recent application records
        """
        sorted_records = sorted(
            self.records, key=lambda r: datetime.fromisoformat(r.timestamp), reverse=True
        )

        return [
            {
                "timestamp": r.timestamp,
                "loan_amount": f"${r.loan_amount:,.0f}",
                "fico_score": r.fico_score,
                "dti_ratio": f"{r.dti_ratio*100:.1f}%",
                "interest_rate": f"{r.interest_rate:.2f}%",
                "risk_level": r.risk_level,
                "prediction": r.prediction,
                "approval_probability": f"{r.approval_probability:.0f}%",
            }
            for r in sorted_records[:limit]
        ]

    def get_approval_trend(self, days: int = 7) -> list[dict]:
        """
        Get approval rate trend over time.

        Parameters
        ----------
        days : int
            Number of days to analyze

        Returns
        -------
        list[dict]
            Daily approval trend data
        """
        trend_data = {}

        cutoff_time = datetime.now() - timedelta(days=days)

        for record in self.records:
            record_time = datetime.fromisoformat(record.timestamp)
            if record_time > cutoff_time:
                date_key = record_time.date().isoformat()

                if date_key not in trend_data:
                    trend_data[date_key] = {"total": 0, "approved": 0, "rejected": 0}

                trend_data[date_key]["total"] += 1
                if record.prediction == "SAFE":
                    trend_data[date_key]["approved"] += 1
                else:
                    trend_data[date_key]["rejected"] += 1

        # Convert to sorted list
        trend_list = []
        for date_key in sorted(trend_data.keys()):
            data = trend_data[date_key]
            approval_rate = (
                round((data["approved"] / data["total"]) * 100, 2) if data["total"] > 0 else 0.0
            )
            trend_list.append(
                {
                    "date": date_key,
                    "total": data["total"],
                    "approved": data["approved"],
                    "rejected": data["rejected"],
                    "approval_rate": approval_rate,
                }
            )

        return trend_list

    def get_loan_amount_distribution(self, hours: int = 24, bins: int = 5) -> list[dict]:
        """
        Get distribution of loan amounts.

        Parameters
        ----------
        hours : int
            Number of hours to look back
        bins : int
            Number of bins for distribution

        Returns
        -------
        list[dict]
            Loan amount distribution
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        filtered_records = [
            r for r in self.records if datetime.fromisoformat(r.timestamp) > cutoff_time
        ]

        if not filtered_records:
            return []

        loan_amounts = [r.loan_amount for r in filtered_records]
        min_loan = min(loan_amounts)
        max_loan = max(loan_amounts)

        bin_width = (max_loan - min_loan) / bins if max_loan > min_loan else 1

        distribution = []
        for i in range(bins):
            bin_min = min_loan + (i * bin_width)
            bin_max = min_loan + ((i + 1) * bin_width)

            count = sum(
                1 for amount in loan_amounts if bin_min <= amount <= (bin_max if i < bins - 1 else float("inf"))
            )

            distribution.append(
                {
                    "range": f"${bin_min:,.0f} - ${bin_max:,.0f}",
                    "min": round(bin_min, 2),
                    "max": round(bin_max, 2),
                    "count": count,
                    "percentage": round((count / len(loan_amounts)) * 100, 2),
                }
            )

        return distribution

    def get_dashboard_summary(self) -> dict:
        """
        Get complete dashboard summary data.

        Returns
        -------
        dict
            Complete dashboard data
        """
        metrics_24h = self.get_metrics(hours=24)
        metrics_7d = self.get_metrics(hours=168)
        risk_dist = self.get_risk_distribution(hours=24)

        return {
            "metrics_24h": {
                "total_applications": metrics_24h.total_applications,
                "approval_rate": f"{metrics_24h.approval_rate * 100:.1f}%",
                "average_loan": f"${metrics_24h.average_loan_amount:,.0f}",
                "average_fico": int(metrics_24h.average_fico_score),
                "average_dti": f"{metrics_24h.average_dti * 100:.1f}%",
                "average_approval_probability": f"{metrics_24h.average_approval_probability:.0f}%",
            },
            "metrics_7d": {
                "total_applications": metrics_7d.total_applications,
                "approval_rate": f"{metrics_7d.approval_rate * 100:.1f}%",
                "average_loan": f"${metrics_7d.average_loan_amount:,.0f}",
                "average_fico": int(metrics_7d.average_fico_score),
            },
            "risk_distribution": {
                "low": f"{risk_dist.low_risk_percentage:.1f}%",
                "medium": f"{risk_dist.medium_risk_percentage:.1f}%",
                "high": f"{risk_dist.high_risk_percentage:.1f}%",
            },
            "recent_applications": self.get_recent_applications(limit=5),
            "approval_trend": self.get_approval_trend(days=7),
        }


# Singleton instance getter
_analytics_instance: Optional[AnalyticsService] = None


def get_analytics_service() -> AnalyticsService:
    """Get or create analytics service singleton."""
    global _analytics_instance
    if _analytics_instance is None:
        _analytics_instance = AnalyticsService()
    return _analytics_instance
