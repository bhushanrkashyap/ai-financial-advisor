package com.financialadvisor.engine.recommendation;

/**
 * Model representing a financial recommendation for a loan application.
 */
public class FinancialRecommendation {
    private final String recommendationType;
    private final String description;
    private final double priority; // 0-1 scale
    private final String action;

    public FinancialRecommendation(
            String recommendationType,
            String description,
            double priority,
            String action) {
        this.recommendationType = recommendationType;
        this.description = description;
        this.priority = Math.max(0, Math.min(1, priority)); // Clamp to 0-1
        this.action = action;
    }

    public String getRecommendationType() {
        return recommendationType;
    }

    public String getDescription() {
        return description;
    }

    public double getPriority() {
        return priority;
    }

    public String getAction() {
        return action;
    }

    @Override
    public String toString() {
        return "FinancialRecommendation{"
                + "type='" + recommendationType + '\''
                + ", description='" + description + '\''
                + ", priority=" + priority
                + ", action='" + action + '\''
                + '}';
    }
}
