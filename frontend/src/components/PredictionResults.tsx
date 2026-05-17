import { useEffect, useRef } from "react";
import "../styles/components.css";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import { Pie, Doughnut, Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

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

  // Risk gauge SVG
  const gaugeCanvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (gaugeCanvasRef.current) {
      const canvas = gaugeCanvasRef.current;
      const ctx = canvas.getContext("2d");
      if (ctx) {
        const value = prediction.default_probability;
        drawGauge(ctx, value, canvas.width, canvas.height);
      }
    }
  }, [prediction.default_probability]);

  const drawGauge = (
    ctx: CanvasRenderingContext2D,
    value: number,
    width: number,
    height: number
  ) => {
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) / 2 - 10;

    // Draw background
    ctx.fillStyle = "#f5f5f5";
    ctx.fillRect(0, 0, width, height);

    // Draw gauge background
    ctx.strokeStyle = "#e0e0e0";
    ctx.lineWidth = 15;
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, Math.PI, 2 * Math.PI);
    ctx.stroke();

    // Draw gauge value
    const color =
      value < 0.3 ? "#2ecc71" : value < 0.6 ? "#f39c12" : "#e74c3c";
    ctx.strokeStyle = color;
    ctx.lineWidth = 15;
    ctx.beginPath();
    ctx.arc(
      centerX,
      centerY,
      radius,
      Math.PI,
      Math.PI + value * Math.PI
    );
    ctx.stroke();

    // Draw text
    ctx.fillStyle = "#333";
    ctx.font = "bold 24px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(`${(value * 100).toFixed(1)}%`, centerX, centerY);

    ctx.font = "12px Arial";
    ctx.fillStyle = "#666";
    ctx.fillText("Default Risk", centerX, centerY + 25);
  };

  // Probability pie chart
  const pieChartData = {
    labels: ["Default Risk", "Safe"],
    datasets: [
      {
        data: [
          prediction.default_probability * 100,
          prediction.safe_probability * 100,
        ],
        backgroundColor: ["#e74c3c", "#2ecc71"],
        borderColor: ["#c0392b", "#27ae60"],
        borderWidth: 2,
      },
    ],
  };

  const pieChartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "bottom" as const,
      },
      title: {
        display: true,
        text: "Probability Distribution",
      },
    },
  };

  return (
    <div className="card results-card">
      <h2>Prediction results</h2>

      {/* Visualizations Section */}
      <div className="result-group">
        <h3>📊 Risk Visualizations</h3>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>
          {/* Gauge Chart */}
          <div>
            <canvas
              ref={gaugeCanvasRef}
              width={250}
              height={150}
              style={{ maxWidth: "100%" }}
            />
          </div>

          {/* Pie Chart */}
          <div>
            <Pie data={pieChartData} options={pieChartOptions} />
          </div>
        </div>

        {/* Confidence Score Visualization */}
        <div className="result-item" style={{ marginTop: "20px" }}>
          <div className="result-label">Model Confidence</div>
          <div className="result-value">{(prediction.confidence_score * 100).toFixed(1)}%</div>
          <div className="confidence-bar-detailed">
            <div
              className="confidence-fill-detailed"
              style={{
                width: `${prediction.confidence_score * 100}%`,
                backgroundColor:
                  prediction.confidence_score > 0.8
                    ? "#2ecc71"
                    : prediction.confidence_score > 0.6
                      ? "#f39c12"
                      : "#e74c3c",
              }}
            />
          </div>
        </div>
      </div>

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
