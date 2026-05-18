import { useState } from "react";
import "./App.css";
import { API_BASE } from "./config";
import { LoanForm } from "./components/LoanForm";
import { PredictionResults } from "./components/PredictionResults";
import { SystemStatus } from "./components/SystemStatus";
import { FinancialSummaryCard } from "./components/FinancialSummaryCard";
import { ApprovalProbabilityGauge } from "./components/ApprovalProbabilityGauge";
import { ImprovementRecommendations } from "./components/ImprovementRecommendations";
import { AnalyticsDashboard } from "./components/AnalyticsDashboard";

interface Prediction {
  prediction: string;
  default_probability: number;
  safe_probability: number;
  risk_level: string;
  recommendation: string;
  confidence_score: number;
}

interface FinancialData {
  loan_amount: number;
  term_months: number;
  interest_rate: number;
  emi_calculation: {
    monthly_emi: number;
    total_amount_payable: number;
    total_interest: number;
    principal: number;
    term_months: number;
    annual_interest_rate: number;
    monthly_interest_rate: number;
  };
  financial_health: {
    dti_ratio: number;
    dti_category: string;
    debt_to_income_percentage: number;
    loan_to_income_ratio: number;
    monthly_income: number;
    monthly_emi: number;
    monthly_remaining_after_emi: number;
    emi_affordability: string;
    financial_health_score: number;
  };
  approval_probability: {
    approval_probability: number;
    approval_category: string;
    composite_score: number;
    component_scores: Record<string, number>;
  };
  recommendations: Array<{
    category: string;
    priority: string;
    recommendation: string;
    potential_impact: string;
    timeline: string;
  }>;
  prediction: Prediction;
}

export function App() {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, unknown> | null>(null);
  const [showAnalytics, setShowAnalytics] = useState(false);

  const handlePredict = async (data: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    setFinancialData(null);
    setFormData(data);

    try {
      // First, get the basic prediction
      const predResponse = await fetch(`${API_BASE}/api/credit/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!predResponse.ok) {
        const detail = await predResponse.text();
        throw new Error(detail ? `${predResponse.status}: ${detail.slice(0, 120)}` : `API error ${predResponse.status}`);
      }

      const result = (await predResponse.json()) as Prediction;
      setPrediction(result);

      // Then, get the enhanced financial summary
      try {
        const financialResponse = await fetch(`${API_BASE}/api/credit/financial-summary`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        if (financialResponse.ok) {
          const financialResult = (await financialResponse.json()) as FinancialData;
          setFinancialData(financialResult);
        }
      } catch (err) {
        // If financial summary fails, continue with just prediction
        console.warn("Failed to fetch financial summary:", err);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="header-brand">
            <h1>💰 Loan Eligibility Checker</h1>
            <p>Check if you qualify for a loan in seconds</p>
          </div>
          <SystemStatus />
        </div>
      </header>

      <div className="container">
        <div className="content">
          <div className="form-section">
            <LoanForm onPredict={handlePredict} loading={loading} />
            
            <button 
              className="analytics-toggle"
              onClick={() => setShowAnalytics(!showAnalytics)}
              style={{
                marginTop: "1rem",
                padding: "0.75rem 1.5rem",
                backgroundColor: showAnalytics ? "#2ecc71" : "#3498db",
                color: "#fff",
                border: "none",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "0.95rem",
                fontWeight: 500,
                transition: "all 0.3s ease",
              }}
            >
              {showAnalytics ? "← Hide Analytics" : "📊 Show Analytics"}
            </button>
          </div>

          <div className="results-section">
            {error && <div className="error">{error}</div>}
            {loading && <div className="loading">Running model and financial analysis…</div>}
            
            {prediction && (
              <>
                {/* Primary Prediction Results */}
                <PredictionResults prediction={prediction} />

                {/* Enhanced Financial Analysis Section */}
                {financialData && (
                  <div className="financial-analysis-section" style={{ marginTop: "2rem" }}>
                    <h2 style={{ marginBottom: "1.5rem", fontSize: "1.3rem", fontWeight: 600 }}>
                      💼 Financial Analysis
                    </h2>

                    {/* Approval Gauge */}
                    <ApprovalProbabilityGauge
                      approval_probability={financialData.approval_probability.approval_probability}
                      approval_category={financialData.approval_probability.approval_category}
                      confidence_score={prediction.confidence_score}
                    />

                    {/* Financial Summary */}
                    <FinancialSummaryCard
                      monthly_emi={financialData.emi_calculation.monthly_emi}
                      total_interest={financialData.emi_calculation.total_interest}
                      total_amount_payable={financialData.emi_calculation.total_amount_payable}
                      term_months={financialData.emi_calculation.term_months}
                      dti_ratio={financialData.financial_health.dti_ratio}
                      dti_category={financialData.financial_health.dti_category}
                      financial_health_score={financialData.financial_health.financial_health_score}
                      emi_affordability={financialData.financial_health.emi_affordability}
                    />

                    {/* Improvement Recommendations */}
                    {financialData.recommendations && financialData.recommendations.length > 0 && (
                      <ImprovementRecommendations recommendations={financialData.recommendations} />
                    )}
                  </div>
                )}
              </>
            )}

            {!prediction && !loading && !error && (
              <div className="card">
                <h2>Results</h2>
                <div className="no-results">
                  Submit a loan application to see risk scores, financial analysis, approval probability, and recommendations.
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Analytics Dashboard - Sidebar */}
        {showAnalytics && (
          <div className="analytics-sidebar">
            <AnalyticsDashboard />
          </div>
        )}
      </div>
    </div>
  );
}
