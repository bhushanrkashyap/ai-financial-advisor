package com.financialadvisor.engine.recommendation;

import java.util.List;

/**
 * Interface for the Financial Advisor Recommendation Engine.
 * 
 * Provides personalized recommendations based on credit risk assessment,
 * loan terms, and financial profile.
 */
public interface IRecommendationEngine {
    /**
     * Generate financial recommendations based on loan application data.
     *
     * @param loanAmount Loan amount in USD
     * @param interestRate Annual interest rate (%)
     * @param term Loan term in months
     * @param defaultProbability Probability of default (0-1)
     * @param riskLevel Risk level classification (LOW_RISK, MEDIUM_RISK, HIGH_RISK)
     * @param ficoScore Applicant's FICO score
     * @param dtiRatio Debt-to-income ratio (0-1)
     * @param annualIncome Annual income in USD
     * @return List of financial recommendations sorted by priority
     */
    List<FinancialRecommendation> generateRecommendations(
            double loanAmount,
            double interestRate,
            int term,
            double defaultProbability,
            String riskLevel,
            int ficoScore,
            double dtiRatio,
            double annualIncome);

    /**
     * Calculate optimal loan term based on financial profile.
     *
     * @param loanAmount Loan amount in USD
     * @param ficoScore Applicant's FICO score
     * @param dtiRatio Debt-to-income ratio
     * @return Recommended loan term in months
     */
    int getOptimalLoanTerm(double loanAmount, int ficoScore, double dtiRatio);

    /**
     * Get recommended interest rate based on risk profile.
     *
     * @param baseRate Base interest rate
     * @param defaultProbability Probability of default
     * @param ficoScore Applicant's FICO score
     * @return Recommended interest rate
     */
    double getRecommendedInterestRate(double baseRate, double defaultProbability, int ficoScore);

    /**
     * Check if loan should be approved based on risk assessment.
     *
     * @param defaultProbability Probability of default
     * @param riskLevel Risk level classification
     * @param dtiRatio Debt-to-income ratio
     * @return true if loan can be approved, false otherwise
     */
    boolean shouldApproveLoan(double defaultProbability, String riskLevel, double dtiRatio);
}
