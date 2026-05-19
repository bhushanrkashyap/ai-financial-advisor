import { useState } from "react";
import { API_BASE } from "../config";

interface Portfolio {
  allocation: Record<string, number>;
  allocation_decimal: Record<string, number>;
  monthly_investment: number;
  annual_investment: number;
  expected_annual_return: number;
  volatility: number;
  sharpe_ratio: number;
  notes: string;
}

type RiskLevel = "conservative" | "moderate" | "aggressive";

export function PortfolioRecommendation() {
  const [riskLevel, setRiskLevel] = useState<RiskLevel>("moderate");
  const [annualIncome, setAnnualIncome] = useState(600000);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getRecommendation = async () => {
    setLoading(true);
    setError(null);
    setPortfolio(null);

    try {
      // Send annual income (backend expects annual income in INR)
      const response = await fetch(
        `${API_BASE}/api/credit/portfolio/recommend?risk_level=${riskLevel}&income=${annualIncome}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) {
        // try to parse error body for friendlier message
        let msg = `API error: ${response.status}`;
        try {
          const errBody = await response.json();
          msg = errBody.detail || errBody.message || msg;
        } catch (_) {}
        throw new Error(msg);
      }

      const data = (await response.json()) as Portfolio;
      setPortfolio(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get recommendation");
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level: RiskLevel) => {
    switch (level) {
      case "conservative":
        return "#27ae60";
      case "moderate":
        return "#f39c12";
      case "aggressive":
        return "#e74c3c";
      default:
        return "#3498db";
    }
  };

  const getRiskDescription = (level: RiskLevel) => {
    switch (level) {
      case "conservative":
        return "Lower risk, steady growth - Best for risk-averse investors";
      case "moderate":
        return "Balanced risk/return - Best for most investors";
      case "aggressive":
        return "Higher risk, higher returns - Best for long-term investors";
      default:
        return "";
    }
  };

  return (
    <div className="card" style={{ marginTop: "2rem" }}>
      <h2>Portfolio Optimization & Allocation</h2>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Get personalized investment allocation using Modern Portfolio Theory
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
            Risk Tolerance Level
          </label>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            {(["conservative", "moderate", "aggressive"] as const).map((level) => (
              <button
                key={level}
                onClick={() => setRiskLevel(level)}
                style={{
                  flex: 1,
                  padding: "0.75rem",
                  backgroundColor: riskLevel === level ? getRiskColor(level) : "#e0e0e0",
                  color: riskLevel === level ? "#fff" : "#333",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: 500,
                  textTransform: "capitalize",
                  transition: "all 0.3s ease",
                }}
              >
                {level}
              </button>
            ))}
          </div>
          <p style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
            {getRiskDescription(riskLevel)}
          </p>
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 600 }}>
            Annual Income (₹)
          </label>
          <input
            type="number"
            value={annualIncome}
            onChange={(e) => setAnnualIncome(parseFloat(e.target.value))}
            placeholder="600000"
            style={{
              width: "100%",
              padding: "0.75rem",
              border: "2px solid #e0e0e0",
              borderRadius: "6px",
              fontSize: "1rem",
            }}
          />
          <p style={{ fontSize: "0.85rem", color: "#666", marginTop: "0.5rem" }}>
            Monthly Income: ₹{(annualIncome / 12).toLocaleString("en-IN", { maximumFractionDigits: 0 })}
          </p>
        </div>
      </div>

      <button
        onClick={getRecommendation}
        disabled={loading}
        style={{
          padding: "0.75rem 2rem",
          backgroundColor: "#3498db",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          cursor: loading ? "not-allowed" : "pointer",
          marginBottom: "1.5rem",
          fontSize: "0.95rem",
          fontWeight: 500,
          opacity: loading ? 0.6 : 1,
        }}
      >
        {loading ? "Calculating..." : "Get Recommendation"}
      </button>

      {error && (
        <div style={{ backgroundColor: "#fee", color: "#c33", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
          Error: {error}
        </div>
      )}

      {portfolio && (
        <div style={{ backgroundColor: "#f5f5f5", padding: "1.5rem", borderRadius: "8px" }}>
          {/* Performance Metrics */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "1.5rem",
              borderRadius: "8px",
              marginBottom: "1.5rem",
            }}
          >
            <h3 style={{ marginBottom: "1rem", color: "var(--text)", fontSize: "0.95rem" }}>Portfolio Performance Metrics</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "1rem",
              }}
            >
              <div style={{ padding: "1rem", backgroundColor: "#f0fff0", borderRadius: "6px" }}>
                <p style={{ color: "#666", marginBottom: "0.25rem", fontSize: "0.85rem" }}>Expected Annual Return</p>
                <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#27ae60" }}>
                  {(portfolio.expected_annual_return * 100).toFixed(2)}%
                </p>
              </div>
              <div style={{ padding: "1rem", backgroundColor: "#f0f8ff", borderRadius: "6px" }}>
                <p style={{ color: "#666", marginBottom: "0.25rem", fontSize: "0.85rem" }}>Risk (Volatility)</p>
                <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e74c3c" }}>
                  {(portfolio.volatility * 100).toFixed(2)}%
                </p>
              </div>
              <div style={{ padding: "1rem", backgroundColor: "#fff0f5", borderRadius: "6px" }}>
                <p style={{ color: "#666", marginBottom: "0.25rem", fontSize: "0.85rem" }}>Sharpe Ratio</p>
                <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#9b59b6" }}>
                  {portfolio.sharpe_ratio.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          {/* Asset Allocation */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "1.5rem",
              borderRadius: "8px",
              marginBottom: "1.5rem",
            }}
          >
            <h3 style={{ marginBottom: "1rem", color: "var(--text)", fontSize: "0.95rem" }}>Recommended Asset Allocation</h3>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
                gap: "1rem",
              }}
            >
              {Object.entries(portfolio.allocation).map(([asset, percentage]) => {
                const colors: Record<string, string> = {
                  stocks: "#3498db",
                  bonds: "#27ae60",
                  gold: "#f39c12",
                  cash: "#95a5a6",
                };
                return (
                  <div key={asset} style={{ textAlign: "center" }}>
                    <div
                      style={{
                        width: "120px",
                        height: "120px",
                        borderRadius: "50%",
                        backgroundColor: colors[asset] || "#3498db",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        margin: "0 auto 0.5rem",
                        color: "#fff",
                        fontSize: "1.5rem",
                        fontWeight: "bold",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                      }}
                    >
                      {(percentage * 100).toFixed(0)}%
                    </div>
                    <p style={{ fontWeight: 600, textTransform: "capitalize", marginBottom: "0.25rem" }}>
                      {asset}
                    </p>
                    <p style={{ fontSize: "0.85rem", color: "#666" }}>
                      ₹{(portfolio.allocation_decimal[asset] * (annualIncome / 12)).toLocaleString("en-IN", {
                        maximumFractionDigits: 0,
                      })}
                      /month
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Investment Summary */}
          <div
            style={{
              backgroundColor: "#fff",
              padding: "1.5rem",
              borderRadius: "8px",
              marginBottom: "1.5rem",
              borderLeft: "4px solid #3498db",
            }}
          >
            <h3 style={{ marginBottom: "1rem", color: "var(--text)", fontSize: "0.95rem" }}>Investment Summary</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
              <div>
                <p style={{ color: "#666", marginBottom: "0.25rem" }}>Monthly Investment</p>
                <p style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#2c3e50" }}>
                  ₹{portfolio.monthly_investment.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div>
                <p style={{ color: "#666", marginBottom: "0.25rem" }}>Annual Investment</p>
                <p style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#2c3e50" }}>
                  ₹{portfolio.annual_investment.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          </div>

          {/* Notes */}
          {portfolio.notes && (
            <div
              style={{
                backgroundColor: "#fffacd",
                padding: "1rem",
                borderRadius: "6px",
                borderLeft: "4px solid #f39c12",
              }}
            >
              <p style={{ fontWeight: 600, marginBottom: "0.5rem", color: "#2c3e50" }}>📝 Portfolio Notes:</p>
              <p style={{ color: "#555", lineHeight: "1.6" }}>{portfolio.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
