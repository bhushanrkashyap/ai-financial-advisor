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
        throw new Error(`API error: ${response.status}`);
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
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Estimate property prices using advanced machine learning models
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div>
          <label>Total Sqft</label>
          <input
            type="number"
            name="total_sqft"
            value={formData.total_sqft}
            onChange={handleInputChange}
            placeholder="1500"
          />
        </div>
        <div>
          <label>BHK</label>
          <input
            type="number"
            name="bhk"
            value={formData.bhk}
            onChange={handleInputChange}
            placeholder="3"
          />
        </div>
        <div>
          <label>Bathrooms</label>
          <input
            type="number"
            name="bath"
            value={formData.bath}
            onChange={handleInputChange}
            placeholder="2"
          />
        </div>
        <div>
          <label>Balcony</label>
          <input
            type="number"
            name="balcony"
            value={formData.balcony}
            onChange={handleInputChange}
            placeholder="1"
          />
        </div>
        <div>
          <label>Price per Sqft (₹)</label>
          <input
            type="number"
            name="price_per_sqft"
            value={formData.price_per_sqft}
            onChange={handleInputChange}
            placeholder="45000"
          />
        </div>
        <div>
          <label>Area Type (0-2)</label>
          <input
            type="number"
            name="area_type_encoded"
            value={formData.area_type_encoded}
            onChange={handleInputChange}
            min="0"
            max="2"
          />
        </div>
        <div>
          <label>Availability (0-3)</label>
          <input
            type="number"
            name="availability_encoded"
            value={formData.availability_encoded}
            onChange={handleInputChange}
            min="0"
            max="3"
          />
        </div>
        <div>
          <label>Location (0-10)</label>
          <input
            type="number"
            name="location_encoded"
            value={formData.location_encoded}
            onChange={handleInputChange}
            min="0"
            max="10"
          />
        </div>
        <div>
          <label>Has Society (0-1)</label>
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

      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem" }}>
        <button
          onClick={() => predictPrice(false)}
          disabled={loading}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: "#3498db",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1,
            fontSize: "0.95rem",
            fontWeight: 500,
          }}
        >
          {loading && useEnsemble === false ? "Predicting..." : "Predict Price"}
        </button>

        <button
          onClick={() => {
            setUseEnsemble(true);
            predictPrice(true);
          }}
          disabled={loading}
          style={{
            padding: "0.75rem 1.5rem",
            backgroundColor: "#27ae60",
            color: "#fff",
            border: "none",
            borderRadius: "8px",
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading ? 0.6 : 1,
            fontSize: "0.95rem",
            fontWeight: 500,
          }}
        >
          {loading && useEnsemble === true ? "Predicting..." : "Ensemble Prediction"}
        </button>
      </div>

      {error && (
        <div style={{ backgroundColor: "#fee", color: "#c33", padding: "1rem", borderRadius: "8px", marginBottom: "1rem" }}>
          Error: {error}
        </div>
      )}

      {prediction && !ensemblePrediction && (
        <div style={{ backgroundColor: "#f0f8ff", padding: "1.5rem", borderRadius: "8px", border: "2px solid #3498db" }}>
          <h3 style={{ marginBottom: "1rem", color: "#2c3e50" }}>📊 Price Prediction</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "1rem",
            }}
          >
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Predicted Price</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#27ae60" }}>
                {formatPrice(prediction.predicted_price)}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Confidence Score</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#3498db" }}>
                {(prediction.confidence * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Price Range</p>
              <p style={{ fontSize: "0.9rem" }}>
                {formatPrice(prediction.uncertainty_range.lower)} - {formatPrice(prediction.uncertainty_range.upper)}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Model Used</p>
              <p style={{ fontSize: "0.95rem", fontWeight: 500 }}>{prediction.model_used}</p>
            </div>
          </div>
        </div>
      )}

      {ensemblePrediction && (
        <div style={{ backgroundColor: "#f0fff0", padding: "1.5rem", borderRadius: "8px", border: "2px solid #27ae60" }}>
          <h3 style={{ marginBottom: "1rem", color: "#2c3e50" }}>🎯 Ensemble Prediction (3 Models)</h3>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Ensemble Price</p>
              <p style={{ fontSize: "1.8rem", fontWeight: "bold", color: "#27ae60" }}>
                {formatPrice(ensemblePrediction.ensemble_price)}
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Consensus Score</p>
              <p style={{ fontSize: "1.5rem", fontWeight: "bold", color: "#3498db" }}>
                {(ensemblePrediction.consensus_score * 100).toFixed(1)}%
              </p>
            </div>
            <div>
              <p style={{ color: "#666", marginBottom: "0.25rem" }}>Standard Deviation</p>
              <p style={{ fontSize: "1rem" }}>{formatPrice(ensemblePrediction.std_deviation)}</p>
            </div>
          </div>

          <div style={{ backgroundColor: "#fff", padding: "1rem", borderRadius: "6px" }}>
            <p style={{ fontWeight: 600, marginBottom: "0.75rem" }}>Individual Model Predictions:</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "1rem" }}>
              {Object.entries(ensemblePrediction.individual_predictions).map(([model, price]) => (
                <div key={model} style={{ backgroundColor: "#f9f9f9", padding: "0.75rem", borderRadius: "6px" }}>
                  <p style={{ fontSize: "0.85rem", color: "#666" }}>{model}</p>
                  <p style={{ fontSize: "1.1rem", fontWeight: "bold", color: "#2c3e50" }}>
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
