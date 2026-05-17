import { useState } from "react";
import "./App.css";
import { API_BASE } from "./config";
import { LoanForm } from "./components/LoanForm";
import { PredictionResults } from "./components/PredictionResults";
import { SystemStatus } from "./components/SystemStatus";
import { ExplainabilityPanel } from "./components/ExplainabilityPanel";
import { FairnessAnalysis } from "./components/FairnessAnalysis";
import { ScenarioAnalysis } from "./components/ScenarioAnalysis";

interface Prediction {
  prediction: string;
  default_probability: number;
  safe_probability: number;
  risk_level: string;
  recommendation: string;
  confidence_score: number;
}

export function App() {
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<Record<string, unknown> | null>(null);

  const handlePredict = async (data: Record<string, unknown>) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    setFormData(data);

    try {
      const response = await fetch(`${API_BASE}/api/credit/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail ? `${response.status}: ${detail.slice(0, 120)}` : `API error ${response.status}`);
      }

      const result = (await response.json()) as Prediction;
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleExplain = async () => {
    if (!formData) throw new Error("No prediction data available");
    try {
      const response = await fetch(`${API_BASE}/api/credit/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to generate explanation");
      return await response.json();
    } catch (err) {
      throw err;
    }
  };

  const handleAnalyzeFairness = async () => {
    if (!formData) throw new Error("No prediction data available");
    try {
      const response = await fetch(`${API_BASE}/api/credit/analyze-fairness`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to analyze fairness");
      return await response.json();
    } catch (err) {
      throw err;
    }
  };

  const handleAnalyzeScenarios = async () => {
    if (!formData) throw new Error("No prediction data available");
    try {
      const response = await fetch(`${API_BASE}/api/credit/scenarios`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error("Failed to analyze scenarios");
      return await response.json();
    } catch (err) {
      throw err;
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="header-brand">
            <h1>AI Financial Advisor</h1>
            <p>Credit risk scoring and recommendation preview powered by your FastAPI and Java services.</p>
          </div>
          <SystemStatus />
        </div>
      </header>

      <div className="container">
        <div className="content">
          <div className="form-section">
            <LoanForm onPredict={handlePredict} loading={loading} />
          </div>

          <div className="results-section">
            {error && <div className="error">{error}</div>}
            {loading && <div className="loading">Running model and recommendation engine…</div>}
            {prediction && (
              <>
                <PredictionResults prediction={prediction} />
                
                {/* Advanced Analysis Features */}
                <div style={{ marginTop: "2rem" }}>
                  <h2 style={{ marginBottom: "1.5rem", fontSize: "1.3rem", fontWeight: 600 }}>
                    ✨ Advanced Analysis
                  </h2>
                  
                  <ExplainabilityPanel prediction={prediction} onExplain={handleExplain} />
                  
                  <FairnessAnalysis onAnalyzeFairness={handleAnalyzeFairness} />
                  
                  <ScenarioAnalysis onAnalyzeScenarios={handleAnalyzeScenarios} />
                </div>
              </>
            )}
            {!prediction && !loading && !error && (
              <div className="card">
                <h2>Results</h2>
                <div className="no-results">
                  Submit the loan application to see risk scores, probabilities, and the blended recommendation.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
