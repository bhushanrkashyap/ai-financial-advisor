import React, { useState } from "react";
import "../styles/components.css";

interface ExplanationProps {
  prediction: {
    default_probability: number;
    risk_level: string;
  };
  onExplain: () => Promise<any>;
}

export function ExplainabilityPanel({ prediction, onExplain }: ExplanationProps) {
  const [explanation, setExplanation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExplain = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await onExplain();
      setExplanation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate explanation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🔍 Model Explainability (SHAP)</h2>
      
      <div className="result-group">
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
          Understand which factors most influenced the prediction
        </p>

        <button
          onClick={handleExplain}
          disabled={loading}
          style={{
            padding: "0.75rem 1.25rem",
            backgroundColor: "#3498db",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? "Generating explanation..." : "Explain This Prediction"}
        </button>

        {error && (
          <div style={{ color: "red", marginTop: "1rem" }}>
            ⚠️ {error}
          </div>
        )}

        {explanation && (
          <div style={{ marginTop: "1.5rem" }}>
            <div className="result-group">
              <h3>🎯 Top Factors</h3>

              {explanation.explanation?.top_features?.map(
                (feature: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      padding: "0.75rem",
                      marginBottom: "0.75rem",
                      backgroundColor: "rgba(0,0,0,0.1)",
                      borderLeft: feature.shap_value > 0 ? "3px solid #e74c3c" : "3px solid #2ecc71",
                      borderRadius: "4px"
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.5rem" }}>
                      <strong>{feature.feature_name.replace(/_/g, " ")}</strong>
                      <span style={{ color: feature.shap_value > 0 ? "#e74c3c" : "#2ecc71" }}>
                        {feature.contribution}
                      </span>
                    </div>
                    <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      Current value: {feature.feature_value.toFixed(2)} | Impact: {feature.shap_value.toFixed(4)}
                    </div>
                  </div>
                )
              )}
            </div>

            <div className="result-group">
              <h3>📊 Summary</h3>
              <p style={{ whiteSpace: "pre-wrap", fontSize: "0.9rem" }}>
                {explanation.explanation?.summary}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
