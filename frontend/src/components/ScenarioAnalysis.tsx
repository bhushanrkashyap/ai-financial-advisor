import React, { useState } from "react";
import "../styles/components.css";

interface ScenarioProps {
  onAnalyzeScenarios: () => Promise<any>;
}

export function ScenarioAnalysis({ onAnalyzeScenarios }: ScenarioProps) {
  const [scenarios, setScenarios] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await onAnalyzeScenarios();
      setScenarios(result);
      setExpandedSection("quick_wins");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze scenarios");
    } finally {
      setLoading(false);
    }
  };

  const getEffortColor = (effort: string) => {
    switch (effort) {
      case "LOW":
        return "#2ecc71";
      case "MEDIUM":
        return "#f39c12";
      case "HIGH":
        return "#e74c3c";
      default:
        return "#95a5a6";
    }
  };

  return (
    <div className="card">
      <h2>🎯 What-If Scenario Analysis</h2>

      <div className="result-group">
        <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
          Explore how improving specific factors can lead to loan approval
        </p>

        <button
          onClick={handleAnalyze}
          disabled={loading}
          style={{
            padding: "0.75rem 1.25rem",
            backgroundColor: "#16a34a",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1
          }}
        >
          {loading ? "Analyzing scenarios..." : "Generate Scenarios"}
        </button>

        {error && (
          <div style={{ color: "red", marginTop: "1rem" }}>
            ⚠️ {error}
          </div>
        )}

        {scenarios && (
          <div style={{ marginTop: "1.5rem" }}>
            {/* Current Status */}
            <div className="result-group">
              <h3>📊 Current Status</h3>

              <div
                style={{
                  padding: "0.75rem",
                  backgroundColor: "rgba(0,0,0,0.1)",
                  borderRadius: "6px"
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span>Current Default Probability:</span>
                  <strong>
                    {(scenarios.scenarios?.current_probability * 100).toFixed(2)}% ({scenarios.scenarios?.current_risk_level})
                  </strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.5rem" }}>
                  <span>Approval Threshold:</span>
                  <strong>{(scenarios.scenarios?.approval_threshold * 100).toFixed(0)}%</strong>
                </div>
              </div>
            </div>

            {/* Best Path to Approval */}
            {scenarios.scenarios?.best_path_to_approval && (
              <div className="result-group">
                <h3>🚀 Best Path to Approval</h3>

                {scenarios.scenarios.best_path_to_approval.quick_wins?.length > 0 && (
                  <div style={{ marginBottom: "1rem" }}>
                    <h4 style={{ margin: "0 0 0.75rem 0", color: "#2ecc71", fontSize: "0.95rem" }}>
                      ✓ Quick Wins (Easiest)
                    </h4>
                    {scenarios.scenarios.best_path_to_approval.quick_wins.map((win: any, idx: number) => (
                      <div
                        key={idx}
                        style={{
                          padding: "0.75rem",
                          marginBottom: "0.5rem",
                          backgroundColor: "rgba(46, 204, 113, 0.1)",
                          border: "1px solid rgba(46, 204, 113, 0.3)",
                          borderRadius: "6px"
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{win.action}</div>
                        <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                          Would reduce default probability to: {(win.final_probability * 100).toFixed(2)}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {scenarios.scenarios.best_path_to_approval.medium_term?.length > 0 && (
                  <div style={{ marginBottom: "1rem" }}>
                    <h4 style={{ margin: "0 0 0.75rem 0", color: "#f39c12", fontSize: "0.95rem" }}>
                      ⚡ Medium Term (3-6 months)
                    </h4>
                    {scenarios.scenarios.best_path_to_approval.medium_term.map((term: any, idx: number) => (
                      <div
                        key={idx}
                        style={{
                          padding: "0.75rem",
                          marginBottom: "0.5rem",
                          backgroundColor: "rgba(243, 156, 18, 0.1)",
                          border: "1px solid rgba(243, 156, 18, 0.3)",
                          borderRadius: "6px"
                        }}
                      >
                        <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{term.action}</div>
                        <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                          Would reduce default probability to: {(term.final_probability * 100).toFixed(2)}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="recommendation-box approved">
                  <strong>Recommended Action:</strong>
                  <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.9rem" }}>
                    {scenarios.scenarios.best_path_to_approval.recommended_action}
                  </p>
                </div>
              </div>
            )}

            {/* All Scenarios */}
            <div className="result-group">
              <h3>📈 Detailed Scenarios</h3>

              {["improve_fico", "reduce_dti", "increase_income", "reduce_loan", "reduce_delinquency"].map(
                (scenarioType) => {
                  const scenarioList = scenarios.scenarios?.scenarios?.[scenarioType] || [];

                  if (scenarioList.length === 0) return null;

                  return (
                    <div key={scenarioType} style={{ marginBottom: "1rem" }}>
                      <button
                        onClick={() =>
                          setExpandedSection(expandedSection === scenarioType ? null : scenarioType)
                        }
                        style={{
                          width: "100%",
                          padding: "0.75rem",
                          backgroundColor: "transparent",
                          border: "1px solid var(--border)",
                          borderRadius: "6px",
                          textAlign: "left",
                          cursor: "pointer",
                          fontWeight: 600,
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center"
                        }}
                      >
                        <span>{scenarioType.replace(/_/g, " ").toUpperCase()}</span>
                        <span>{expandedSection === scenarioType ? "▼" : "▶"}</span>
                      </button>

                      {expandedSection === scenarioType && (
                        <div style={{ marginTop: "0.75rem" }}>
                          {scenarioList.map((scenario: any, idx: number) => (
                            <div
                              key={idx}
                              style={{
                                padding: "0.75rem",
                                marginBottom: "0.5rem",
                                backgroundColor: "rgba(0,0,0,0.05)",
                                borderLeft: `3px solid ${getEffortColor(scenario.effort)}`,
                                borderRadius: "4px"
                              }}
                            >
                              <div style={{ fontWeight: 600, marginBottom: "0.25rem" }}>{scenario.action}</div>
                              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                                Effort: <strong>{scenario.effort}</strong> | Impact: {scenario.probability_reduction.toFixed(1)}% reduction
                              </div>
                              <div style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginTop: "0.25rem" }}>
                                New probability: {(scenario.new_probability * 100).toFixed(2)}%
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
