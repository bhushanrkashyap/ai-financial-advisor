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
      <h2>💼 Investment Portfolio</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem", fontSize: "0.95rem" }}>
        Get personalized investment allocation using Modern Portfolio Theory
      </p>

      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1.5rem", marginBottom: "1.5rem" }}>
        <div>
          <label style={{ display: "block", marginBottom: "0.8rem", fontWeight: 700, color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "0.04em" }}>
            🎯 Risk Tolerance Level
          </label>
          <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap" }}>
            {(["conservative", "moderate", "aggressive"] as const).map((level) => (
              <button
                key={level}
                onClick={() => setRiskLevel(level)}
                style={{
                  flex: "1 1 130px",
                  padding: "0.85rem 1rem",
                  backgroundColor: riskLevel === level ? getRiskColor(level) : "rgba(255,255,255,0.05)",
                  color: riskLevel === level ? "#fff" : "var(--text-secondary)",
                  border: riskLevel === level ? "none" : "1.5px solid var(--border)",
                  borderRadius: "var(--radius-md)",
                  cursor: "pointer",
                  fontWeight: 700,
                  textTransform: "capitalize",
                  transition: "all var(--transition-base)",
                  fontSize: "0.9rem",
                  boxShadow: riskLevel === level ? `0 6px 20px ${getRiskColor(level)}40` : "none",
                }}
              >
                {level}
              </button>
            ))}
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--text-tertiary)", marginTop: "0.8rem" }}>
            {getRiskDescription(riskLevel)}
          </p>
        </div>

        <div className="form-group">
          <label>💰 Annual Income (₹)</label>
          <input
            type="number"
            value={annualIncome}
            onChange={(e) => setAnnualIncome(parseFloat(e.target.value))}
            placeholder="600000"
          />
          <p style={{ fontSize: "0.85rem", color: "var(--text-tertiary)", marginTop: "0.5rem" }}>
            📅 Monthly Income: <strong style={{ color: "var(--text)" }}>₹{(annualIncome / 12).toLocaleString("en-IN", { maximumFractionDigits: 0 })}</strong>
          </p>
        </div>
      </div>

      <button
        onClick={getRecommendation}
        disabled={loading}
        className="submit-btn"
        style={{ width: "100%", marginBottom: "1.5rem" }}
      >
        {loading ? "⏳ Calculating..." : "✨ Get Recommendation"}
      </button>

      {error && (
        <div style={{ background: "var(--danger-dim)", color: "var(--danger)", padding: "1rem", borderRadius: "var(--radius-md)", marginBottom: "1rem", border: "1px solid var(--danger)" }}>
          ⚠️ Error: {error}
        </div>
      )}

      {portfolio && (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          {/* Performance Metrics */}
          <div className="result-group">
            <h3>📊 Portfolio Performance Metrics</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1.2rem" }}>
              <div style={{ padding: "1.2rem", background: "linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05))", borderRadius: "var(--radius-md)", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
                <p className="result-label">Expected Annual Return</p>
                <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--success)" }}>
                  {(portfolio.expected_annual_return * 100).toFixed(2)}%
                </p>
              </div>
              <div style={{ padding: "1.2rem", background: "linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05))", borderRadius: "var(--radius-md)", border: "1px solid rgba(239, 68, 68, 0.2)" }}>
                <p className="result-label">Risk (Volatility)</p>
                <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--danger)" }}>
                  {(portfolio.volatility * 100).toFixed(2)}%
                </p>
              </div>
              <div style={{ padding: "1.2rem", background: "linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(6, 182, 212, 0.05))", borderRadius: "var(--radius-md)", border: "1px solid rgba(6, 182, 212, 0.2)" }}>
                <p className="result-label">Sharpe Ratio</p>
                <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--accent)" }}>
                  {portfolio.sharpe_ratio.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          {/* Asset Allocation */}
          <div className="result-group">
            <h3>🎯 Recommended Asset Allocation</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "1.5rem" }}>
              {Object.entries(portfolio.allocation).map(([asset, percentage]) => {
                const colors: Record<string, string> = {
                  stocks: "#06b6d4",
                  bonds: "#10b981",
                  gold: "#f59e0b",
                  cash: "#8b5cf6",
                };
                return (
                  <div key={asset} style={{ textAlign: "center" }}>
                    <div
                      style={{
                        width: "120px",
                        height: "120px",
                        borderRadius: "50%",
                        background: `linear-gradient(135deg, ${colors[asset] || "#3498db"}, ${colors[asset] || "#3498db"}dd)`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        margin: "0 auto 0.8rem",
                        color: "#fff",
                        fontSize: "2rem",
                        fontWeight: "bold",
                        boxShadow: `0 8px 24px ${colors[asset] || "#3498db"}40`,
                        transition: "all var(--transition-base)",
                        cursor: "pointer",
                      }}
                      onMouseEnter={(e) => {
                        (e.target as HTMLElement).style.transform = "scale(1.05)";
                        (e.target as HTMLElement).style.boxShadow = `0 12px 32px ${colors[asset] || "#3498db"}60`;
                      }}
                      onMouseLeave={(e) => {
                        (e.target as HTMLElement).style.transform = "scale(1)";
                        (e.target as HTMLElement).style.boxShadow = `0 8px 24px ${colors[asset] || "#3498db"}40`;
                      }}
                    >
                      {(percentage * 100).toFixed(0)}%
                    </div>
                    <p style={{ fontWeight: 700, textTransform: "capitalize", marginBottom: "0.5rem", color: "var(--text)" }}>
                      {asset}
                    </p>
                    <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
                      ₹{(portfolio.allocation_decimal[asset] * (annualIncome / 12)).toLocaleString("en-IN", {
                        maximumFractionDigits: 0,
                      })}/month
                    </p>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Investment Summary */}
          <div className="result-group" style={{ borderLeft: "4px solid var(--accent)" }}>
            <h3>💡 Investment Summary</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.5rem" }}>
              <div>
                <p className="result-label">Monthly Investment</p>
                <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--accent)" }}>
                  ₹{portfolio.monthly_investment.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </p>
              </div>
              <div>
                <p className="result-label">Annual Investment</p>
                <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--accent)" }}>
                  ₹{portfolio.annual_investment.toLocaleString("en-IN", { maximumFractionDigits: 0 })}
                </p>
              </div>
            </div>
          </div>

          {/* Notes */}
          {portfolio.notes && (
            <div style={{ background: "linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0.05))", padding: "1.2rem", borderRadius: "var(--radius-md)", borderLeft: "4px solid var(--warning)" }}>
              <p style={{ fontWeight: 700, marginBottom: "0.8rem", color: "var(--text)", fontSize: "0.95rem" }}>📝 Portfolio Recommendations:</p>
              <p style={{ color: "var(--text-secondary)", lineHeight: 1.6 }}>{portfolio.notes}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
