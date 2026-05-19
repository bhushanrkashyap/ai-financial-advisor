import { useState } from "react";
import { API_BASE } from "../config";

interface HousePriceFormData {
  total_sqft: number;
  bhk: number;
  bath: number;
  balcony: number;
  price_per_sqft: number;
  area_type_encoded: number;
  availability_encoded: number;
  location_encoded: number;
  has_society: number;
}

interface HousePricePrediction {
  predicted_price: number;
  confidence: number;
  uncertainty: number;
  uncertainty_range: {
    lower: number;
    upper: number;
  };
  model_used: string;
}

interface EnsemblePrediction extends HousePricePrediction {
  ensemble_price: number;
  individual_predictions: Record<string, number>;
  consensus_score: number;
  std_deviation: number;
}

export function HousePricePrediction() {
  const [formData, setFormData] = useState<HousePriceFormData>({
    total_sqft: 1500,
    bhk: 3,
    bath: 2,
    balcony: 1,
    price_per_sqft: 45000,
    area_type_encoded: 1,
    availability_encoded: 2,
    location_encoded: 5,
    has_society: 1,
  });

  const [prediction, setPrediction] = useState<HousePricePrediction | null>(null);
  const [ensemblePrediction, setEnsemblePrediction] = useState<EnsemblePrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [useEnsemble, setUseEnsemble] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: parseFloat(value),
    }));
  };

  const predictPrice = async (ensemble: boolean = false) => {
    setLoading(true);
    setError(null);
    setPrediction(null);
    setEnsemblePrediction(null);

    try {
      const endpoint = ensemble
        ? `${API_BASE}/api/credit/collateral/ensemble-estimate`
        : `${API_BASE}/api/credit/collateral/estimate-house-price`;

      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        let msg = `API error: ${response.status}`;
        try {
          const errBody = await response.json();
          msg = errBody.detail || errBody.message || msg;
        } catch (_) {}
        throw new Error(msg);
      }

      const data = (await response.json()) as HousePricePrediction | EnsemblePrediction;

      if (ensemble) {
        setEnsemblePrediction(data as EnsemblePrediction);
      } else {
        setPrediction(data as HousePricePrediction);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price: number) => {
    if (price >= 10000000) {
      return `₹${(price / 10000000).toFixed(2)} Cr`;
    } else if (price >= 100000) {
      return `₹${(price / 100000).toFixed(2)} L`;
    } else {
      return `₹${price.toFixed(0)}`;
    }
  };

  return (
    <div className="card" style={{ marginTop: "2rem" }}>
      <h2>🏠 House Price Prediction</h2>
      <p style={{ color: "var(--text-secondary)", marginBottom: "1.5rem", fontSize: "0.95rem" }}>
        Estimate property prices using advanced machine learning models
      </p>

      <div className="form-row" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "1.2rem", marginBottom: "1.5rem" }}>
        <div className="form-group">
          <label>📐 Total Sqft</label>
          <input
            type="number"
            name="total_sqft"
            value={formData.total_sqft}
            onChange={handleInputChange}
            placeholder="1500"
          />
        </div>
        <div className="form-group">
          <label>🏢 BHK</label>
          <input
            type="number"
            name="bhk"
            value={formData.bhk}
            onChange={handleInputChange}
            placeholder="3"
          />
        </div>
        <div className="form-group">
          <label>🚿 Bathrooms</label>
          <input
            type="number"
            name="bath"
            value={formData.bath}
            onChange={handleInputChange}
            placeholder="2"
          />
        </div>
        <div className="form-group">
          <label>🌳 Balcony</label>
          <input
            type="number"
            name="balcony"
            value={formData.balcony}
            onChange={handleInputChange}
            placeholder="1"
          />
        </div>
        <div className="form-group">
          <label>💰 Price per Sqft (₹)</label>
          <input
            type="number"
            name="price_per_sqft"
            value={formData.price_per_sqft}
            onChange={handleInputChange}
            placeholder="45000"
          />
        </div>
        <div className="form-group">
          <label>🏘️ Area Type (0-2)</label>
          <input
            type="number"
            name="area_type_encoded"
            value={formData.area_type_encoded}
            onChange={handleInputChange}
            min="0"
            max="2"
          />
        </div>
        <div className="form-group">
          <label>📅 Availability (0-3)</label>
          <input
            type="number"
            name="availability_encoded"
            value={formData.availability_encoded}
            onChange={handleInputChange}
            min="0"
            max="3"
          />
        </div>
        <div className="form-group">
          <label>📍 Location (0-10)</label>
          <input
            type="number"
            name="location_encoded"
            value={formData.location_encoded}
            onChange={handleInputChange}
            min="0"
            max="10"
          />
        </div>
        <div className="form-group">
          <label>🏘️ Has Society (0-1)</label>
          <input
            type="number"
            name="has_society"
            value={formData.has_society}
            onChange={handleInputChange}
            min="0"
            max="1"
          />
        </div>
      </div>

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
        <button
          onClick={() => predictPrice(false)}
          disabled={loading}
          className="submit-btn"
          style={{ flex: "1 1 auto", minWidth: "150px" }}
        >
          {loading && useEnsemble === false ? "Predicting..." : "💡 Predict Price"}
        </button>

        <button
          onClick={() => {
            setUseEnsemble(true);
            predictPrice(true);
          }}
          disabled={loading}
          className="submit-btn"
          style={{ 
            flex: "1 1 auto",
            minWidth: "150px",
            background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
            boxShadow: "0 6px 20px rgba(16, 185, 129, 0.25)",
          }}
        >
          {loading && useEnsemble === true ? "Predicting..." : "🎯 Ensemble"}
        </button>
      </div>

      {error && (
        <div style={{ background: "var(--danger-dim)", color: "var(--danger)", padding: "1rem", borderRadius: "var(--radius-md)", marginBottom: "1rem", border: "1px solid var(--danger)" }}>
          ⚠️ Error: {error}
        </div>
      )}

      {loading && !prediction && !ensemblePrediction && (
        <div style={{ background: "linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(6, 182, 212, 0.04))", padding: "1.2rem", borderRadius: "var(--radius-md)", marginBottom: "1rem", color: "var(--text-secondary)", border: "1px solid rgba(6, 182, 212, 0.2)" }}>
          ⏳ Predicting price — this may take a moment. If external services are unavailable, a model-only estimate will be shown.
        </div>
      )}

      {prediction && !ensemblePrediction && (
        <div className="result-group">
          <h3>💰 Price Prediction</h3>
          <div className="form-row" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.5rem", marginBottom: 0 }}>
            <div>
              <p className="result-label">Predicted Price</p>
              <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--success)" }}>
                {formatPrice(prediction.predicted_price)}
              </p>
            </div>
            <div>
              <p className="result-label">Confidence Score</p>
              <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--accent)" }}>
                {(prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="result-label">Price Range</p>
              <p style={{ fontSize: "0.95rem", color: "var(--text)" }}>
                {formatPrice(prediction.uncertainty_range.lower)} - {formatPrice(prediction.uncertainty_range.upper)}
              </p>
            </div>
            <div>
              <p className="result-label">Model Used</p>
              <p style={{ fontSize: "0.95rem", fontWeight: 500, color: "var(--text)" }}>{prediction.model_used}</p>
            </div>
          </div>
        </div>
      )}

      {ensemblePrediction && (
        <div className="result-group">
          <h3>🎯 Ensemble Prediction (3 Models)</h3>
          <div className="form-row" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1.5rem", marginBottom: "1.5rem" }}>
            <div>
              <p className="result-label">Ensemble Price</p>
              <p style={{ fontSize: "2rem", fontWeight: "bold", color: "var(--success)" }}>
                {formatPrice(ensemblePrediction.ensemble_price)}
              </p>
            </div>
            <div>
              <p className="result-label">Consensus Score</p>
              <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "var(--accent)" }}>
                {(ensemblePrediction.consensus_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p className="result-label">Standard Deviation</p>
              <p style={{ fontSize: "1rem", color: "var(--text)" }}>{formatPrice(ensemblePrediction.std_deviation)}</p>
            </div>
          </div>

          <div style={{ background: "rgba(6, 182, 212, 0.05)", padding: "1.2rem", borderRadius: "var(--radius-md)", border: "1px solid rgba(6, 182, 212, 0.15)" }}>
            <p style={{ fontWeight: 700, marginBottom: "1rem", color: "var(--text)", fontSize: "0.95rem" }}>📊 Individual Model Predictions:</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
              {Object.entries(ensemblePrediction.individual_predictions).map(([model, price]) => (
                <div key={model} style={{ background: "var(--surface-elevated)", padding: "1rem", borderRadius: "var(--radius-md)", border: "1px solid var(--border)", transition: "all var(--transition-base)" }}>
                  <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.5rem" }}>{model}</p>
                  <p style={{ fontSize: "1.2rem", fontWeight: "bold", color: "var(--accent)" }}>
                    {formatPrice(price as number)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
