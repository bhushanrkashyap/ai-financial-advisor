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
import { HousePricePrediction } from "./components/HousePricePrediction";
import { PortfolioRecommendation } from "./components/PortfolioRecommendation";

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
            <h1>🤖 AI Financial Advisor</h1>
            <p>Intelligent predictions for loans, properties, and investments</p>
          </div>
          <SystemStatus />
        </div>
      </header>

      <div className="container">
        <div className="three-block-layout" style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(400px, 1fr))",
          gap: "2rem",
          padding: "2rem 0"
        }}>
          {/* BLOCK 1: LOAN PREDICTION */}
          <div style={{
            backgroundColor: "#f8f9fa",
            border: "3px solid #3498db",
            borderRadius: "12px",
            padding: "2rem",
            boxShadow: "0 4px 12px rgba(52, 152, 219, 0.15)"
          }}>
            <h2 style={{
              fontSize: "1.3rem",
              marginBottom: "1rem",
              color: "#2c3e50",
              textAlign: "center",
              fontWeight: 700
            }}>💼 Loan Prediction</h2>
            
            <div className="form-section">
              <LoanForm onPredict={handlePredict} loading={loading} />
              
              <button 
                className="analytics-toggle"
                onClick={() => setShowAnalytics(!showAnalytics)}
                style={{
                  marginTop: "1rem",
                  width: "100%",
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

            {/* Loan Prediction Results */}
            {error && <div className="error" style={{ marginTop: "1rem" }}>{error}</div>}
            {loading && <div className="loading" style={{ marginTop: "1rem" }}>Analyzing application…</div>}
            
            {prediction && (
              <div style={{ marginTop: "1.5rem" }}>
                <PredictionResults prediction={prediction} />

                {financialData && (
                  <div className="financial-analysis-section" style={{ marginTop: "1.5rem" }}>
                    <ApprovalProbabilityGauge
                      approval_probability={financialData.approval_probability.approval_probability}
                      approval_category={financialData.approval_probability.approval_category}
                      confidence_score={prediction.confidence_score}
                    />

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

                    {financialData.recommendations && financialData.recommendations.length > 0 && (
                      <ImprovementRecommendations recommendations={financialData.recommendations} />
                    )}
                  </div>
                )}
              </div>
            )}

            {!prediction && !loading && !error && (
              <div style={{
                marginTop: "1.5rem",
                padding: "1rem",
                backgroundColor: "#e8f4f8",
                borderRadius: "8px",
                textAlign: "center",
                color: "#555",
                fontSize: "0.9rem"
              }}>
                Submit a loan application to see predictions
              </div>
            )}
          </div>

          {/* BLOCK 2: HOUSE PRICE PREDICTION */}
          <div style={{
            backgroundColor: "#f8f9fa",
            border: "3px solid #27ae60",
            borderRadius: "12px",
            padding: "2rem",
            boxShadow: "0 4px 12px rgba(39, 174, 96, 0.15)",
            maxHeight: "fit-content"
          }}>
            <h2 style={{
              fontSize: "1.3rem",
              marginBottom: "1rem",
              color: "#2c3e50",
              textAlign: "center",
              fontWeight: 700
            }}>🏠 House Price Prediction</h2>
            
            <HousePricePrediction />
          </div>

          {/* BLOCK 3: INVESTMENT & PORTFOLIO */}
          <div style={{
            backgroundColor: "#f8f9fa",
            border: "3px solid #9b59b6",
            borderRadius: "12px",
            padding: "2rem",
            boxShadow: "0 4px 12px rgba(155, 89, 182, 0.15)",
            maxHeight: "fit-content"
          }}>
            <h2 style={{
              fontSize: "1.3rem",
              marginBottom: "1rem",
              color: "#2c3e50",
              textAlign: "center",
              fontWeight: 700
            }}>📊 Investment Portfolio</h2>
            
            <PortfolioRecommendation />
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
