import React, { useState } from "react";
import "../styles/components.css";

interface FairnessProps {
  onAnalyzeFairness: () => Promise<any>;
}

export function FairnessAnalysis({ onAnalyzeFairness }: FairnessProps) {
  const [fairness, setFairness] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await onAnalyzeFairness();
      setFairness(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze fairness");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "LOW":
        return "#2ecc71";
      case "MEDIUM":
        return "#f39c12";
      case "HIGH":
        return "#e74c3c";
      case "CRITICAL":
        return "#c0392b";
      default:
        return "#95a5a6";
    }
  };

  const getBiasColor = (bias: string) => {
    switch (bias) {
      case "FAIR":
        return "#2ecc71";
      case "MINOR_BIAS":
        return "#f39c12";
      case "MODERATE_BIAS":
        return "#e67e22";
      case "SEVERE_BIAS":
        return "#e74c3c";
      default:
        return "#95a5a6";
    }
  };

  return (
    <div className="card">
      <h2>Fairness & Bias Analysis</h2>

      <div className="result-group">
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
          Check for potential discrimination and lending bias
        </p>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            padding: "0.75rem 1.25rem",
            backgroundColor: "#9b59b6",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? "Analyzing fairness..." : "Analyze Fairness"}
        </button>

        {error && (
          <div style={{ color: "red", marginTop: "1rem" }}>
            {error}
          </div>
        )}

        {fairness && (
          <div style={{ marginTop: "1.5rem" }}>
            {/* Bias Score */}
            <div className="result-group">
              <h3>Bias Assessment</h3>

              <div
                style={{
                  padding: "1rem",
                  backgroundColor: getBiasColor(fairness.fairness_analysis?.bias_level) + "20",
                  border: `2px solid ${getBiasColor(fairness.fairness_analysis?.bias_level)}`,
                  borderRadius: "8px",
                  marginBottom: "1rem"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <strong style={{ fontSize: "1rem" }}>Bias Level</strong>
                    <div style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
                      {fairness.fairness_analysis?.bias_level}
                    </div>
                  </div>
                  <div style={{ fontSize: "2rem", color: getBiasColor(fairness.fairness_analysis?.bias_level) }}>
                    {(fairness.fairness_analysis?.bias_score * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>

            {/* Discrimination Risk */}
            <div className="result-group">
              <h3>Discrimination Risk</h3>

              <div
                style={{
                  padding: "0.75rem",
                  backgroundColor: getRiskColor(fairness.fairness_analysis?.discrimination_risk_level) + "20",
                  border: `2px solid ${getRiskColor(fairness.fairness_analysis?.discrimination_risk_level)}`,
                  borderRadius: "6px",
                  marginBottom: "1rem"
                }}
              >
                <strong>{fairness.fairness_analysis?.discrimination_risk_level}</strong>
              </div>

              <div className="result-item">
                <div className="result-label">Fairness Checks</div>
                {fairness.fairness_analysis?.fairness_checks && (
                  <ul style={{ margin: "0.5rem 0", paddingLeft: "1.5rem" }}>
                    {Object.entries(fairness.fairness_analysis.fairness_checks).map(([key, value]: [string, any]) => (
                      <li key={key} style={{ marginBottom: "0.25rem", color: value ? "#e74c3c" : "#2ecc71" }}>
                          {key.replace(/_/g, " ")}: {value ? "Flag" : "Pass"}
                        </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* Recommendations */}
            <div className="result-group">
              <h3>💡 Recommendations</h3>
              <div className="recommendation-box approved">
                <p style={{ margin: "0", fontSize: "0.9rem", lineHeight: "1.6" }}>
                  {fairness.fairness_analysis?.fairness_recommendation}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
