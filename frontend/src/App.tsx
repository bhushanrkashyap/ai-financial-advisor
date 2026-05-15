import { useState } from 'react';
import './App.css';
import { LoanForm } from './components/LoanForm';
import { PredictionResults } from './components/PredictionResults';

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

  const handlePredict = async (formData: Record<string, any>) => {
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const response = await fetch('http://localhost:8000/api/credit/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      const result = await response.json();
      setPrediction(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>💰 AI Financial Advisor</h1>
        <p>Credit Risk Assessment & Financial Recommendations Platform</p>
      </header>

      <div className="container">
        <div className="content">
          <div className="form-section">
            <LoanForm onPredict={handlePredict} loading={loading} />
          </div>

          <div className="results-section">
            {error && <div className="error">{error}</div>}
            {loading && <div className="loading">Processing...</div>}
            {prediction && <PredictionResults prediction={prediction} />}
            {!prediction && !loading && !error && (
              <div className="no-results">
                <p>Fill in the loan details and submit to see predictions</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
