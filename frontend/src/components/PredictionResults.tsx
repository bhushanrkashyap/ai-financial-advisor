import '../styles/components.css';

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

export function PredictionResults({ prediction }: PredictionResultsProps) {
  const getRiskClass = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW_RISK':
        return 'risk-low';
      case 'MEDIUM_RISK':
        return 'risk-medium';
      case 'HIGH_RISK':
        return 'risk-high';
      default:
        return 'risk-low';
    }
  };

  const getRecommendationClass = (riskLevel: string) => {
    if (riskLevel === 'LOW_RISK') return 'approved';
    if (riskLevel === 'MEDIUM_RISK') return 'review';
    return 'denied';
  };

  return (
    <div className="card results-card">
      <h2>📊 Prediction Results</h2>

      <div className="result-group">
        <h3>Risk Assessment</h3>

        <div className="result-item">
          <div className="result-label">Risk Level</div>
          <div className="result-value">
            <span className={`risk-badge ${getRiskClass(prediction.risk_level)}`}>
              {prediction.risk_level.replace('_', ' ')}
            </span>
          </div>
        </div>

        <div className="result-item">
          <div className="result-label">Default Probability</div>
          <div className="result-value">{(prediction.default_probability * 100).toFixed(2)}%</div>
          <div className="probability-bar">
            <div
              className="probability-fill"
              style={{ width: `${prediction.default_probability * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="result-item">
          <div className="result-label">Safe Probability</div>
          <div className="result-value">{(prediction.safe_probability * 100).toFixed(2)}%</div>
        </div>

        <div className="result-item">
          <div className="result-label">Confidence Score</div>
          <div className="result-value">{(prediction.confidence_score * 100).toFixed(1)}%</div>
        </div>
      </div>

      <div className="result-group">
        <h3>Recommendation</h3>
        <div className={`recommendation-box ${getRecommendationClass(prediction.risk_level)}`}>
          <strong>
            {prediction.risk_level === 'LOW_RISK'
              ? '✅ APPROVED'
              : prediction.risk_level === 'MEDIUM_RISK'
                ? '⚠️ REVIEW RECOMMENDED'
                : '❌ DENIAL RECOMMENDED'}
          </strong>
          <p>{prediction.recommendation}</p>
        </div>
      </div>

      <div className="result-group">
        <h3>Action Items</h3>
        <div className="recommendation-box approved">
          <strong>Next Step</strong>
          <p>
            {prediction.risk_level === 'LOW_RISK'
              ? 'Loan can proceed for approval. Standard terms apply.'
              : prediction.risk_level === 'MEDIUM_RISK'
                ? 'Conduct additional review. May require rate adjustment or documentation.'
                : 'Consider loan restructuring or alternative products.'}
          </p>
        </div>
      </div>
    </div>
  );
}
