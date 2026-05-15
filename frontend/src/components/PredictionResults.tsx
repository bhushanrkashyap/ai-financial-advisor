import "../styles/components.css";

interface PredictionResultsProps {
  prediction: {
    prediction: string;
    default_probability: number;
    safe_probability: number;
    risk_level: string;
    recommendation: string;
    confidence_score: number;
  };
}

function formatRiskLabel(riskLevel: string): string {
  return riskLevel.replace(/_/g, " ");
}

export function PredictionResults({ prediction }: PredictionResultsProps) {
  const getRiskClass = (riskLevel: string) => {
    switch (riskLevel) {
      case "LOW_RISK":
        return "risk-low";
      case "MEDIUM_RISK":
        return "risk-medium";
      case "HIGH_RISK":
        return "risk-high";
      default:
        return "risk-low";
    }
  };

  const getRecommendationClass = (riskLevel: string) => {
    if (riskLevel === "LOW_RISK") return "approved";
    if (riskLevel === "MEDIUM_RISK") return "review";
    return "denied";
  };

  return (
    <div className="card results-card">
      <h2>Prediction results</h2>

      <div className="result-group">
        <h3>Risk</h3>

        <div className="result-item">
          <div className="result-label">Level</div>
          <div className="result-value">
            <span className={`risk-badge ${getRiskClass(prediction.risk_level)}`}>{formatRiskLabel(prediction.risk_level)}</span>
          </div>
        </div>

        <div className="result-item">
          <div className="result-label">Default probability</div>
          <div className="result-value">{(prediction.default_probability * 100).toFixed(2)}%</div>
          <div className="probability-bar">
            <div className="probability-fill" style={{ width: `${Math.min(100, prediction.default_probability * 100)}%` }} />
          </div>
        </div>

        <div className="result-item">
          <div className="result-label">Safe probability</div>
          <div className="result-value">{(prediction.safe_probability * 100).toFixed(2)}%</div>
        </div>

        <div className="result-item">
          <div className="result-label">Model confidence</div>
          <div className="result-value">{(prediction.confidence_score * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="result-group">
        <h3>Recommendation</h3>
        <div className={`recommendation-box ${getRecommendationClass(prediction.risk_level)}`}>
          <strong>
            {prediction.risk_level === "LOW_RISK"
              ? "Favorable"
              : prediction.risk_level === "MEDIUM_RISK"
                ? "Review suggested"
                : "High caution"}
          </strong>
          <p>{prediction.recommendation}</p>
        </div>
      </div>

      <div className="result-group">
        <h3>Next steps</h3>
        <div className="recommendation-box approved">
          <strong>Underwriting</strong>
          <p>
            {prediction.risk_level === "LOW_RISK"
              ? "Proceed with standard approval workflow and documentation."
              : prediction.risk_level === "MEDIUM_RISK"
                ? "Request additional documentation or pricing adjustments before final approval."
                : "Consider restructuring, collateral, or alternate products before committing."}
          </p>
        </div>
      </div>
    </div>
  );
}
