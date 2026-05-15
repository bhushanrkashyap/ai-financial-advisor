package com.financialadvisor.engine.dto;

import com.financialadvisor.engine.recommendation.FinancialRecommendation;
import java.io.Serializable;
import java.util.List;

/**
 * Response DTO containing financial recommendations and analysis.
 */
public class RecommendationResponse implements Serializable {

    private List<FinancialRecommendation> recommendations;
    private String primaryRecommendation;
    private int optimalTerm;
    private double recommendedInterestRate;
    private boolean shouldApprove;

    // Getters and Setters
    public List<FinancialRecommendation> getRecommendations() {
        return recommendations;
    }

    public void setRecommendations(List<FinancialRecommendation> recommendations) {
        this.recommendations = recommendations;
    }

    public String getPrimaryRecommendation() {
        return primaryRecommendation;
    }

    public void setPrimaryRecommendation(String primaryRecommendation) {
        this.primaryRecommendation = primaryRecommendation;
    }

    public int getOptimalTerm() {
        return optimalTerm;
    }

    public void setOptimalTerm(int optimalTerm) {
        this.optimalTerm = optimalTerm;
    }

    public double getRecommendedInterestRate() {
        return recommendedInterestRate;
    }

    public void setRecommendedInterestRate(double recommendedInterestRate) {
        this.recommendedInterestRate = recommendedInterestRate;
    }

    public boolean isShouldApprove() {
        return shouldApprove;
    }

    public void setShouldApprove(boolean shouldApprove) {
        this.shouldApprove = shouldApprove;
    }
}
