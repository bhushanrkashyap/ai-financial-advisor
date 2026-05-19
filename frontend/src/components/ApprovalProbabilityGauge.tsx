import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import "../styles/components.css";

interface ApprovalGaugeProps {
  approval_probability: number;
  approval_category: string;
  confidence_score: number;
}

export function ApprovalProbabilityGauge({
  approval_probability,
  approval_category,
  confidence_score,
}: ApprovalGaugeProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    let current = 0;

    const animate = () => {
      interval = setInterval(() => {
        if (current < approval_probability) {
          current += approval_probability / 30;
          setDisplayValue(Math.min(current, approval_probability));
        } else {
          clearInterval(interval);
        }
      }, 20);
    };

    animate();
    return () => clearInterval(interval);
  }, [approval_probability]);

  const getGaugeColor = (value: number): string => {
    if (value >= 80) return "#2ecc71";
    if (value >= 65) return "#3498db";
    if (value >= 50) return "#f39c12";
    if (value >= 35) return "#e67e22";
    return "#e74c3c";
  };

  const getCategoryLabel = (category: string): string => {
    switch (category) {
      case "HIGHLY_LIKELY":
        return "Highly Likely";
      case "LIKELY":
        return "Likely";
      case "POSSIBLE":
        return "Possible";
      case "UNLIKELY":
        return "Unlikely";
      case "VERY_UNLIKELY":
        return "Very Unlikely";
      default:
        return "Unknown";
    }
  };

  const getCategoryIcon = (category: string): string => {
    switch (category) {
      case "HIGHLY_LIKELY":
        return "✓";
      case "LIKELY":
        return "✓";
      case "POSSIBLE":
        return "~";
      case "UNLIKELY":
        return "✗";
      case "VERY_UNLIKELY":
        return "✗";
      default:
        return "?";
    }
  };

  const gaugeAngle = (displayValue / 100) * 180 - 90;

  return (
    <motion.div
      className="card approval-gauge-card"
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="card-header">
        <h3>Approval Probability</h3>
      </div>

      <div className="gauge-container">
        <svg className="gauge-svg" viewBox="0 0 200 120">
          {/* Background arc */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            stroke="#2a2f44"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
          />

          {/* Colored arcs */}
          <path
            d="M 20 100 A 80 80 0 0 1 60 32"
            stroke="#e74c3c"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 60 32 A 80 80 0 0 1 100 16"
            stroke="#e67e22"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 100 16 A 80 80 0 0 1 140 32"
            stroke="#f39c12"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 140 32 A 80 80 0 0 1 160 60"
            stroke="#3498db"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            opacity="0.3"
          />
          <path
            d="M 160 60 A 80 80 0 0 1 180 100"
            stroke="#2ecc71"
            strokeWidth="8"
            fill="none"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* Needle */}
          <g transform={`rotate(${gaugeAngle} 100 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="30"
              stroke={getGaugeColor(displayValue)}
              strokeWidth="4"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="6" fill={getGaugeColor(displayValue)} />
          </g>

          {/* Center circle */}
          <circle cx="100" cy="100" r="12" fill="#1a1f36" stroke={getGaugeColor(displayValue)} strokeWidth="2" />

          {/* Percentage text */}
          <text x="100" y="110" textAnchor="middle" className="gauge-text" fill={getGaugeColor(displayValue)}>
            {Math.round(displayValue)}%
          </text>
        </svg>
      </div>

      <div className="gauge-info">
        <div className="gauge-category">
          <span className="category-icon">{getCategoryIcon(approval_category)}</span>
          <span className="category-label">{getCategoryLabel(approval_category)}</span>
        </div>

        <div className="confidence-info">
          <span className="confidence-label">Model Confidence</span>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${Math.min(100, confidence_score * 100)}%`,
                backgroundColor: confidence_score >= 0.7 ? "#2ecc71" : confidence_score >= 0.5 ? "#f39c12" : "#e74c3c",
              }}
            />
          </div>
          <span className="confidence-value">{(confidence_score * 100).toFixed(0)}%</span>
        </div>
      </div>

      <div className="gauge-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#e74c3c" }} />
          <span>Very Unlikely (&lt;35%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#f39c12" }} />
          <span>Possible (35-65%)</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: "#2ecc71" }} />
          <span>Highly Likely (&gt;80%)</span>
        </div>
      </div>
    </motion.div>
  );
}
