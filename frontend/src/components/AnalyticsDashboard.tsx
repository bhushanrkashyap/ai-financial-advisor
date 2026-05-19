import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { API_BASE } from "../config";
import "../styles/components.css";

interface Metrics24h {
  total_applications: number;
  approval_rate: string;
  average_loan: string;
  average_fico: number;
  average_dti: string;
  average_approval_probability: string;
}

interface Metrics7d {
  total_applications: number;
  approval_rate: string;
  average_loan: string;
  average_fico: number;
}

interface RiskDistribution {
  low: string;
  medium: string;
  high: string;
}

interface RecentApp {
  timestamp: string;
  loan_amount: string;
  fico_score: number;
  dti_ratio: string;
  interest_rate: string;
  risk_level: string;
  prediction: string;
  approval_probability: string;
}

interface TrendDay {
  date: string;
  total: number;
  approved: number;
  rejected: number;
  approval_rate: number;
}

interface DashboardData {
  metrics_24h: Metrics24h;
  metrics_7d: Metrics7d;
  risk_distribution: RiskDistribution;
  recent_applications: RecentApp[];
  approval_trend: TrendDay[];
}

export function AnalyticsDashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/credit/analytics/dashboard-summary`);
      if (!response.ok) throw new Error("Failed to fetch dashboard data");
      const data = await response.json();
      setDashboardData(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card analytics-card">
        <div className="loading-state">Loading analytics...</div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="card analytics-card">
        <div className="error-state">Failed to load analytics</div>
      </div>
    );
  }

  const getRiskColor = (percentage: string): string => {
    const num = parseFloat(percentage);
    if (percentage.includes("high")) return "#e74c3c";
    if (num >= 50) return "#2ecc71";
    if (num >= 25) return "#3498db";
    return "#f39c12";
  };

  return (
    <motion.div
      className="card analytics-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="card-header">
        <h3>Analytics Dashboard</h3>
        <button
          className="refresh-btn"
          onClick={fetchDashboardData}
          title="Refresh data"
        >
          Refresh
        </button>
      </div>

      {/* 24-Hour Metrics */}
      <div className="dashboard-section">
        <h4 className="section-title">Last 24 Hours</h4>
          <div className="metrics-grid">
          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Applications</span>
            <span className="metric-value">{dashboardData.metrics_24h.total_applications}</span>
          </div>

          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Approval Rate</span>
            <span className="metric-value">{dashboardData.metrics_24h.approval_rate}</span>
          </div>

          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Avg Loan</span>
            <span className="metric-value">{dashboardData.metrics_24h.average_loan}</span>
          </div>

          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Avg FICO</span>
            <span className="metric-value">{dashboardData.metrics_24h.average_fico}</span>
          </div>

          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Avg DTI</span>
            <span className="metric-value">{dashboardData.metrics_24h.average_dti}</span>
          </div>

          <div className="metric-card">
            <span className="metric-icon" />
            <span className="metric-label">Avg Approval Prob</span>
            <span className="metric-value">{dashboardData.metrics_24h.average_approval_probability}</span>
          </div>
        </div>
      </div>

      {/* 7-Day Metrics */}
      <div className="dashboard-section">
        <h4 className="section-title">Last 7 Days</h4>
        <div className="metrics-grid compact">
          <div className="metric-card small">
            <span className="metric-label">Applications</span>
            <span className="metric-value">{dashboardData.metrics_7d.total_applications}</span>
          </div>

          <div className="metric-card small">
            <span className="metric-label">Approval Rate</span>
            <span className="metric-value">{dashboardData.metrics_7d.approval_rate}</span>
          </div>

          <div className="metric-card small">
            <span className="metric-label">Avg Loan</span>
            <span className="metric-value">{dashboardData.metrics_7d.average_loan}</span>
          </div>

          <div className="metric-card small">
            <span className="metric-label">Avg FICO</span>
            <span className="metric-value">{dashboardData.metrics_7d.average_fico}</span>
          </div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="dashboard-section">
        <h4 className="section-title">Risk Distribution (24h)</h4>
        <div className="risk-distribution">
          <div className="risk-item">
            <span className="risk-label">Low Risk</span>
            <div className="risk-bar">
              <div className="risk-fill" style={{ width: dashboardData.risk_distribution.low, backgroundColor: "#2ecc71" }} />
            </div>
            <span className="risk-value">{dashboardData.risk_distribution.low}</span>
          </div>

          <div className="risk-item">
            <span className="risk-label">Medium Risk</span>
            <div className="risk-bar">
              <div className="risk-fill" style={{ width: dashboardData.risk_distribution.medium, backgroundColor: "#f39c12" }} />
            </div>
            <span className="risk-value">{dashboardData.risk_distribution.medium}</span>
          </div>

          <div className="risk-item">
            <span className="risk-label">High Risk</span>
            <div className="risk-bar">
              <div className="risk-fill" style={{ width: dashboardData.risk_distribution.high, backgroundColor: "#e74c3c" }} />
            </div>
            <span className="risk-value">{dashboardData.risk_distribution.high}</span>
          </div>
        </div>
      </div>

      {/* Recent Applications */}
      <div className="dashboard-section">
        <h4 className="section-title">Recent Applications</h4>
        <div className="recent-applications-table">
          <div className="table-header">
            <span className="col col-time">Time</span>
            <span className="col col-loan">Loan</span>
            <span className="col col-fico">FICO</span>
            <span className="col col-dti">DTI</span>
            <span className="col col-risk">Risk</span>
            <span className="col col-prediction">Result</span>
          </div>

          {dashboardData.recent_applications.map((app, idx) => {
            const timeStr = new Date(app.timestamp).toLocaleTimeString();
            return (
              <div key={idx} className="table-row">
                <span className="col col-time">{timeStr}</span>
                <span className="col col-loan">{app.loan_amount}</span>
                <span className="col col-fico">{app.fico_score}</span>
                <span className="col col-dti">{app.dti_ratio}</span>
                <span
                  className="col col-risk"
                  style={{
                    color:
                      app.risk_level === "LOW_RISK"
                        ? "#2ecc71"
                        : app.risk_level === "HIGH_RISK"
                          ? "#e74c3c"
                          : "#f39c12",
                  }}
                >
                  {app.risk_level.replace(/_/g, " ")}
                </span>
                <span
                  className="col col-prediction"
                  style={{
                    color: app.prediction === "SAFE" ? "#2ecc71" : "#e74c3c",
                    fontWeight: "bold",
                  }}
                >
                  {app.prediction}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Approval Trend */}
      {dashboardData.approval_trend.length > 0 && (
        <div className="dashboard-section">
          <h4 className="section-title">Approval Trend (7 Days)</h4>
          <div className="trend-items">
            {dashboardData.approval_trend.map((day, idx) => (
              <div key={idx} className="trend-item">
                <span className="trend-date">{day.date}</span>
                <div className="trend-stats">
                  <span className="trend-stat">
                    Total: <strong>{day.total}</strong>
                  </span>
                  <span className="trend-stat approve">
                    ✓ <strong>{day.approved}</strong>
                  </span>
                  <span className="trend-stat reject">
                    ✗ <strong>{day.rejected}</strong>
                  </span>
                  <span className="trend-rate">
                    Rate: <strong>{day.approval_rate.toFixed(1)}%</strong>
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
