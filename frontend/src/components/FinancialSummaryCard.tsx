import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import "../styles/components.css";

interface FinancialSummaryProps {
  monthly_emi: number;
  total_interest: number;
  total_amount_payable: number;
  term_months: number;
  dti_ratio: number;
  dti_category: string;
  financial_health_score: number;
  emi_affordability: string;
}

export function FinancialSummaryCard({ 
  monthly_emi, 
  total_interest, 
  total_amount_payable, 
  term_months,
  dti_ratio,
  dti_category,
  financial_health_score,
  emi_affordability
}: FinancialSummaryProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const getDTICategoryColor = (category: string): string => {
    switch (category) {
      case "EXCELLENT":
        return "#2ecc71";
      case "GOOD":
        return "#3498db";
      case "FAIR":
        return "#f39c12";
      case "POOR":
        return "#e74c3c";
      default:
        return "#95a5a6";
    }
  };

  const getDTICategoryLabel = (category: string): string => {
    switch (category) {
      case "EXCELLENT":
        return "Excellent";
      case "GOOD":
        return "Good";
      case "FAIR":
        return "Fair";
      case "POOR":
        return "Poor";
      default:
        return "Unknown";
    }
  };

  const getAffordabilityLabel = (affordability: string): string => {
    switch (affordability) {
      case "HIGHLY_AFFORDABLE":
        return "Highly Affordable";
      case "AFFORDABLE":
        return "Affordable";
      case "TIGHT":
        return "Tight Budget";
      case "UNSUSTAINABLE":
        return "Unsustainable";
      default:
        return "Unknown";
    }
  };

  return (
    <motion.div
      className="card financial-summary-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="card-header">
        <h3>💰 Financial Summary</h3>
        <button
          className="expand-btn"
          onClick={() => setIsExpanded(!isExpanded)}
          aria-label="Toggle details"
        >
          {isExpanded ? "−" : "+"}
        </button>
      </div>

      <div className="financial-grid">
        <div className="financial-item">
          <span className="financial-label">Monthly EMI</span>
          <span className="financial-value">₹{monthly_emi.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
          <span className="financial-subtext">per month</span>
        </div>

        <div className="financial-item">
          <span className="financial-label">Total Interest</span>
          <span className="financial-value">₹{total_interest.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
          <span className="financial-subtext">over {term_months} months</span>
        </div>

        <div className="financial-item">
          <span className="financial-label">Total Payable</span>
          <span className="financial-value">₹{total_amount_payable.toLocaleString("en-IN", { maximumFractionDigits: 0 })}</span>
          <span className="financial-subtext">loan term</span>
        </div>

        <div className="financial-item">
          <span className="financial-label">Financial Health</span>
          <div className="health-score-container">
            <div className="health-score-bar">
              <div
                className="health-score-fill"
                style={{
                  width: `${Math.min(100, financial_health_score)}%`,
                  backgroundColor: financial_health_score >= 70 ? "#2ecc71" : financial_health_score >= 50 ? "#f39c12" : "#e74c3c",
                }}
              />
            </div>
            <span className="health-score-text">{Math.round(financial_health_score)}/100</span>
          </div>
        </div>
      </div>

      {isExpanded && (
        <motion.div
          className="financial-details"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          transition={{ duration: 0.3 }}
        >
          <div className="detail-row">
            <span className="detail-label">DTI Ratio</span>
            <span className="detail-value">
              {(dti_ratio * 100).toFixed(1)}%
              <span
                className="dti-badge"
                style={{ backgroundColor: getDTICategoryColor(dti_category) }}
              >
                {getDTICategoryLabel(dti_category)}
              </span>
            </span>
          </div>

          <div className="detail-row">
            <span className="detail-label">EMI Affordability</span>
            <span className="detail-value">{getAffordabilityLabel(emi_affordability)}</span>
          </div>

          <div className="detail-row">
            <span className="detail-label">Recommended DTI (for best rates)</span>
            <span className="detail-value">Below 36%</span>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
