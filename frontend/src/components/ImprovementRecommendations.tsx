import React, { useState } from "react";
import { motion } from "framer-motion";
import "../styles/components.css";

interface Recommendation {
  category: string;
  priority: string;
  recommendation: string;
  potential_impact: string;
  timeline: string;
}

interface ImprovementRecommendationsProps {
  recommendations: Recommendation[];
}

export function ImprovementRecommendations({
  recommendations,
}: ImprovementRecommendationsProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case "CRITICAL":
        return "#e74c3c";
      case "HIGH":
        return "#e67e22";
      case "MEDIUM":
        return "#f39c12";
      case "LOW":
        return "#3498db";
      default:
        return "#95a5a6";
    }
  };

  const getPriorityIcon = (priority: string): string => {
    switch (priority) {
      case "CRITICAL":
        return "";
      case "HIGH":
        return "";
      case "MEDIUM":
        return "";
      case "LOW":
        return "";
      default:
        return "";
    }
  };

  const getCategoryIcon = (category: string): string => {
    switch (category) {
      case "CREDIT_SCORE":
        return "";
      case "DEBT_TO_INCOME":
        return "";
      case "PAYMENT_HISTORY":
        return "";
      case "EMPLOYMENT":
        return "";
      case "OVERALL_RISK":
        return "";
      default:
        return "";
    }
  };

  const getCategoryLabel = (category: string): string => {
    switch (category) {
      case "CREDIT_SCORE":
        return "Credit Score";
      case "DEBT_TO_INCOME":
        return "Debt-to-Income Ratio";
      case "PAYMENT_HISTORY":
        return "Payment History";
      case "EMPLOYMENT":
        return "Employment Stability";
      case "OVERALL_RISK":
        return "Overall Risk";
      default:
        return category;
    }
  };

  if (!recommendations || recommendations.length === 0) {
    return (
      <motion.div
        className="card improvements-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="card-header">
          <h3>Improvement Recommendations</h3>
        </div>
        <div className="no-recommendations">
          <span>Your application looks great! No improvements needed at this time.</span>
        </div>
      </motion.div>
    );
  }

  const criticalCount = recommendations.filter((r) => r.priority === "CRITICAL").length;
  const highCount = recommendations.filter((r) => r.priority === "HIGH").length;

  return (
    <motion.div
      className="card improvements-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="card-header">
        <h3>Improvement Recommendations</h3>
        {(criticalCount > 0 || highCount > 0) && (
          <span className="recommendation-badge">
            {criticalCount} Critical, {highCount} High Priority
          </span>
        )}
      </div>

      <div className="recommendations-summary">
        <div className="summary-item">
          <span className="summary-label">Total Recommendations</span>
          <span className="summary-value">{recommendations.length}</span>
        </div>
        {criticalCount > 0 && (
          <div className="summary-item critical">
            <span className="summary-label">Critical Issues</span>
            <span className="summary-value">{criticalCount}</span>
          </div>
        )}
        {highCount > 0 && (
          <div className="summary-item high">
            <span className="summary-label">High Priority</span>
            <span className="summary-value">{highCount}</span>
          </div>
        )}
      </div>

      <div className="recommendations-list">
        {recommendations.map((rec, idx) => (
          <motion.div
            key={`${rec.category}-${idx}`}
            className="recommendation-item"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            onClick={() =>
              setSelectedCategory(
                selectedCategory === rec.category ? null : rec.category
              )
            }
            style={{
              borderLeftColor: getPriorityColor(rec.priority),
            }}
          >
            <div className="recommendation-header">
              <div className="recommendation-title">
                <span className="category-icon">{getCategoryIcon(rec.category)}</span>
                <span className="category-name">{getCategoryLabel(rec.category)}</span>
              </div>
              <span className="priority-badge" style={{ backgroundColor: getPriorityColor(rec.priority) }}>
                {getPriorityIcon(rec.priority)} {rec.priority}
              </span>
            </div>

            <div className="recommendation-text">
              <p>{rec.recommendation}</p>
            </div>

            {selectedCategory === rec.category && (
              <motion.div
                className="recommendation-details"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                transition={{ duration: 0.3 }}
              >
                <div className="detail-item">
                  <span className="detail-label">Potential Impact:</span>
                  <span className="detail-value">{rec.potential_impact}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Timeline:</span>
                  <span className="detail-value">{rec.timeline}</span>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="improvements-footer">
        <p className="footer-text">
          Click on any recommendation to see details about potential impact and timeline.
        </p>
      </div>
    </motion.div>
  );
}
