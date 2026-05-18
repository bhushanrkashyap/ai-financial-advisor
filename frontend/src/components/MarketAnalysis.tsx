import { useState, useEffect } from "react";
import { API_BASE } from "../config";

interface MarketConditions {
  volatility_30d: number;
  volatility_regime: string;
  momentum_30d: number;
  market_trend: string;
  vix_equivalent: number;
  market_stress: number;
  date: string;
}

interface Sector {
  symbol: string;
  volatility_30d: number;
  momentum_30d: number;
  latest_return: number;
  performance: string;
}

interface SectorAnalysis {
  sectors: Sector[];
  avg_volatility: number;
  market_health_score: number;
  num_sectors: number;
}

interface LoanDefaultRisk {
  macro_risk_score: number;
  market_adjusted_risk: number;
  risk_category: string;
  vix_equivalent: number;
  volatility_factor: number;
  income_stability_score: number;
  recommendation: string;
}

export function MarketAnalysis() {
  const [marketConditions, setMarketConditions] = useState<MarketConditions | null>(null);
  const [sectorAnalysis, setSectorAnalysis] = useState<SectorAnalysis | null>(null);
  const [loanRisk, setLoanRisk] = useState<LoanDefaultRisk | null>(null);
  const [loading, setLoading] = useState(false);
  const [borrowerIncome, setBorrowerIncome] = useState(500000);
  const [error, setError] = useState<string | null>(null);

  const fetchMarketData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Fetch market conditions
      const condResponse = await fetch(`${API_BASE}/api/credit/market/conditions`);
      if (condResponse.ok) {
        const condData = (await condResponse.json()) as MarketConditions;
        setMarketConditions(condData);
      }

      // Fetch sector analysis
      const sectorResponse = await fetch(`${API_BASE}/api/credit/market/sector-analysis`);
      if (sectorResponse.ok) {
        const sectorData = (await sectorResponse.json()) as SectorAnalysis;
        setSectorAnalysis(sectorData);
      }

      // Fetch loan default risk
      const riskResponse = await fetch(
        `${API_BASE}/api/credit/market/loan-default-risk?borrower_income=${borrowerIncome}`
      );
      if (riskResponse.ok) {
        const riskData = (await riskResponse.json()) as LoanDefaultRisk;
        setLoanRisk(riskData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch market data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMarketData();
  }, []);

  const getTrendColor = (trend: string) => {
    if (trend?.includes("bull") || trend?.includes("up")) return "#27ae60";
    if (trend?.includes("bear") || trend?.includes("down")) return "#e74c3c";
    return "#f39c12";
  };

  const getRiskColor = (category: string) => {
    if (category === "low") return "#27ae60";
    if (category === "moderate") return "#f39c12";
    return "#e74c3c";
  };

  return (
    <div className="card" style={{ marginTop: "2rem" }}>
      <h2>📈 Market Analysis & Stock Price Insights</h2>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Real-time market conditions, sector analysis, and market-adjusted loan risk
      </p>

      <button
        onClick={fetchMarketData}
        disabled={loading}
        style={{
          padding: "0.75rem 1.5rem",
          backgroundColor: "#3498db",
          color: "#fff",
          border: "none",
          borderRadius: "8px",
          cursor: loading ? "not-allowed" : "pointer",
          marginBottom: "1.5rem",
          fontSize: "0.95rem",
          fontWeight: 500,
        }}
      >
        {loading ? "Loading..." : "🔄 Refresh Market Data"}
      </button>

      {error && (
        <div style={{ backgroundColor: "#fee", color: "#c33", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
          Error: {error}
        </div>
      )}

      {/* Market Conditions */}
      {marketConditions && (
        <div style={{ backgroundColor: "#f0f8ff", padding: "1.5rem", borderRadius: "8px", marginBottom: "1.5rem" }}>
          <h3 style={{ marginBottom: "1rem", color: "#2c3e50" }}>🌍 Current Market Conditions</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
              gap: "1rem",
            }}
          >
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Volatility (30d)</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e74c3c" }}>
                {(marketConditions.volatility_30d * 100).toFixed(2)}%
              </p>
              <p style={{ fontSize: "0.85rem", color: "#666" }}>{marketConditions.volatility_regime}</p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Momentum (30d)</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
                {(marketConditions.momentum_30d * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Market Trend</p>
              <p
                style={{
                  fontSize: "1.3rem",
                  fontWeight: "bold",
                  color: getTrendColor(marketConditions.market_trend),
                  textTransform: "capitalize",
                }}
              >
                {marketConditions.market_trend}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>VIX (Market Fear)</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#9b59b6" }}>
                {marketConditions.vix_equivalent.toFixed(2)}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Market Stress</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e67e22" }}>
                {(marketConditions.market_stress * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Last Updated</p>
              <p style={{ fontSize: "0.9rem" }}>{new Date(marketConditions.date).toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Sector Analysis */}
      {sectorAnalysis && (
        <div style={{ backgroundColor: "#fff0f5", padding: "1.5rem", borderRadius: "8px", marginBottom: "1.5rem" }}>
          <h3 style={{ marginBottom: "1rem", color: "#2c3e50" }}>📊 Sector Performance & Stock Analysis</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Average Volatility</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e74c3c" }}>
                {(sectorAnalysis.avg_volatility * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Market Health Score</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#27ae60" }}>
                {(sectorAnalysis.market_health_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Sectors Tracked</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#3498db" }}>
                {sectorAnalysis.num_sectors}
              </p>
            </div>
          </div>

          <div style={{ backgroundColor: "#fff", padding: "1rem", borderRadius: "6px" }}>
            <p style={{ fontWeight: 600, marginBottom: "0.75rem" }}>Stock Performance:</p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: "1rem",
              }}
            >
              {sectorAnalysis.sectors.map((sector) => (
                <div key={sector.symbol} style={{ backgroundColor: "#f9f9f9", padding: "1rem", borderRadius: "6px" }}>
                  <p style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.5rem" }}>{sector.symbol}</p>
                  <div style={{ fontSize: "0.85rem", color: "#666", lineHeight: "1.6" }}>
                    <p>📈 Return: {(sector.latest_return * 100).toFixed(2)}%</p>
                    <p>📊 Vol: {(sector.volatility_30d * 100).toFixed(2)}%</p>
                    <p>Momentum: {(sector.momentum_30d * 100).toFixed(2)}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Loan Default Risk */}
      {loanRisk && (
        <div style={{ backgroundColor: "#f0fff0", padding: "1.5rem", borderRadius: "8px" }}>
          <h3 style={{ marginBottom: "1rem", color: "#2c3e50" }}>⚠️ Market-Adjusted Loan Risk</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Risk Category</p>
              <p
                style={{
                  fontSize: "1.3rem",
                  fontWeight: "bold",
                  color: getRiskColor(loanRisk.risk_category),
                  textTransform: "capitalize",
                }}
              >
                {loanRisk.risk_category}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Market-Adjusted Risk</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#e74c3c" }}>
                {(loanRisk.market_adjusted_risk * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Macro Risk Score</p>
              <p style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#9b59b6" }}>
                {(loanRisk.macro_risk_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Income Stability</p>
              <p style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#27ae60" }}>
                {(loanRisk.income_stability_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          <div style={{ backgroundColor: "#fff", padding: "1rem", borderRadius: "6px", borderLeft: "4px solid #3498db" }}>
            <p style={{ fontWeight: 600, marginBottom: "0.5rem" }}>💡 Recommendation:</p>
            <p style={{ color: "#2c3e50", lineHeight: "1.6" }}>{loanRisk.recommendation}</p>
          </div>

          <div style={{ marginTop: "1rem", fontSize: "0.85rem", color: "#666" }}>
            <p>
              <strong>Borrower Annual Income:</strong> ₹{(borrowerIncome * 12).toLocaleString()}
            </p>
            <p>
              <strong>Volatility Factor:</strong> {(loanRisk.volatility_factor * 100).toFixed(2)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
