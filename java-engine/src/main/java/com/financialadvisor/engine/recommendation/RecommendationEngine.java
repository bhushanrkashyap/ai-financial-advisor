package com.financialadvisor.engine.recommendation;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.logging.Logger;

/**
 * Implementation of the Financial Advisor Recommendation Engine.
 * 
 * Provides intelligent recommendations for loan terms, interest rates,
 * and risk mitigation strategies based on financial analysis.
 */
public class RecommendationEngine implements IRecommendationEngine {
    private static final Logger logger = Logger.getLogger(RecommendationEngine.class.getName());

    private static final double HIGH_RISK_THRESHOLD = 0.6;
    private static final double MEDIUM_RISK_THRESHOLD = 0.3;
    private static final double MAX_DTI_RATIO = 0.43; // Industry standard
    private static final double EXCELLENT_FICO = 740;
    private static final double GOOD_FICO = 670;

    @Override
    public List<FinancialRecommendation> generateRecommendations(
            double loanAmount,
            double interestRate,
            int term,
            double defaultProbability,
            String riskLevel,
            int ficoScore,
            double dtiRatio,
            double annualIncome) {

        List<FinancialRecommendation> recommendations = new ArrayList<>();

        // Risk-based recommendations
        recommendations.addAll(generateRiskRecommendations(defaultProbability, riskLevel));

        // DTI-based recommendations
        recommendations.addAll(generateDTIRecommendations(dtiRatio, loanAmount, annualIncome));

        // FICO-based recommendations
        recommendations.addAll(generateFICORecommendations(ficoScore));

        // Interest rate recommendations
        recommendations.addAll(generateInterestRateRecommendations(interestRate, defaultProbability));

        // Term recommendations
        recommendations.addAll(generateTermRecommendations(term, loanAmount, interestRate));

        // Sort by priority (descending)
        recommendations.sort(Comparator.comparingDouble(FinancialRecommendation::getPriority).reversed());

        logger.info(String.format("Generated %d recommendations for loan: $%.2f at %.2f%% interest", 
                recommendations.size(), loanAmount, interestRate));

        return recommendations;
    }

    @Override
    public int getOptimalLoanTerm(double loanAmount, int ficoScore, double dtiRatio) {
        // Lower FICO score → longer term to reduce monthly payment → lower DTI
        if (ficoScore < GOOD_FICO) {
            return 60; // Longer term for riskier applicants
        } else if (ficoScore < EXCELLENT_FICO) {
            return 48;
        } else {
            return 36; // Shorter term for excellent credit
        }
    }

    @Override
    public double getRecommendedInterestRate(
            double baseRate, double defaultProbability, int ficoScore) {
        // Add risk premium based on default probability
        double riskPremium = defaultProbability * 5.0; // Up to 5% increase

        // Adjust based on FICO score (already factored into model, but add safety margin)
        double ficoAdjustment = 0;
        if (ficoScore < 600) {
            ficoAdjustment = 2.0;
        } else if (ficoScore < 650) {
            ficoAdjustment = 1.5;
        } else if (ficoScore < 700) {
            ficoAdjustment = 0.5;
        }

        return Math.max(baseRate, baseRate + riskPremium + ficoAdjustment);
    }

    @Override
    public boolean shouldApproveLoan(
            double defaultProbability, String riskLevel, double dtiRatio) {
        // Deny if default probability is too high
        if (defaultProbability > HIGH_RISK_THRESHOLD) {
            return false;
        }

        // Deny if DTI is too high
        if (dtiRatio > MAX_DTI_RATIO) {
            return false;
        }

        // High risk but within threshold can be approved with conditions
        return !"HIGH_RISK".equals(riskLevel) || defaultProbability <= 0.5;
    }

    private List<FinancialRecommendation> generateRiskRecommendations(
            double defaultProbability, String riskLevel) {
        List<FinancialRecommendation> recommendations = new ArrayList<>();

        if ("HIGH_RISK".equals(riskLevel)) {
            recommendations.add(
                    new FinancialRecommendation(
                            "HIGH_RISK_MITIGATION",
                            "This application carries elevated default risk. Consider requiring additional security or co-signer.",
                            0.95,
                            "REQUIRE_COLLATERAL_OR_COSIGNER"));

            recommendations.add(
                    new FinancialRecommendation(
                            "RISK_PRICING",
                            "Apply risk-based pricing adjustment (additional 2-3% to interest rate).",
                            0.90,
                            "INCREASE_INTEREST_RATE"));

        } else if ("MEDIUM_RISK".equals(riskLevel)) {
            recommendations.add(
                    new FinancialRecommendation(
                            "MEDIUM_RISK_REVIEW",
                            "Applicant shows moderate default risk. Recommend thorough documentation review.",
                            0.85,
                            "CONDUCT_ADDITIONAL_REVIEW"));

            recommendations.add(
                    new FinancialRecommendation(
                            "MODERATE_PRICING",
                            "Apply moderate pricing adjustment (additional 0.5-1.5% to interest rate).",
                            0.75,
                            "ADJUST_INTEREST_RATE"));

        } else {
            recommendations.add(
                    new FinancialRecommendation(
                            "LOW_RISK_APPROVAL",
                            "Low default risk identified. Favorable terms can be offered.",
                            0.80,
                            "APPROVE_FAVORABLE_TERMS"));
        }

        return recommendations;
    }

    private List<FinancialRecommendation> generateDTIRecommendations(
            double dtiRatio, double loanAmount, double annualIncome) {
        List<FinancialRecommendation> recommendations = new ArrayList<>();

        if (dtiRatio > MAX_DTI_RATIO) {
            recommendations.add(
                    new FinancialRecommendation(
                            "HIGH_DTI",
                            String.format("Debt-to-income ratio of %.1f%% exceeds acceptable threshold of 43%%.",
                                    dtiRatio * 100),
                            0.92,
                            "REDUCE_LOAN_AMOUNT_OR_REQUIRE_DEBT_PAYOFF"));

        } else if (dtiRatio > 0.35) {
            recommendations.add(
                    new FinancialRecommendation(
                            "ELEVATED_DTI",
                            String.format("Debt-to-income ratio of %.1f%% is elevated. Monitor carefully.",
                                    dtiRatio * 100),
                            0.70,
                            "MONITOR_DTI_CAREFULLY"));

        } else {
            recommendations.add(
                    new FinancialRecommendation(
                            "HEALTHY_DTI",
                            String.format("Healthy debt-to-income ratio of %.1f%%.", dtiRatio * 100),
                            0.65,
                            "APPROVED_DTI_PROFILE"));
        }

        return recommendations;
    }

    private List<FinancialRecommendation> generateFICORecommendations(int ficoScore) {
        List<FinancialRecommendation> recommendations = new ArrayList<>();

        if (ficoScore >= 740) {
            recommendations.add(
                    new FinancialRecommendation(
                            "EXCELLENT_CREDIT",
                            "Excellent credit profile. Offer best available rates and terms.",
                            0.88,
                            "OFFER_PREMIUM_RATES"));

        } else if (ficoScore >= 670) {
            recommendations.add(
                    new FinancialRecommendation(
                            "GOOD_CREDIT",
                            "Good credit history. Standard terms apply with possible discounts.",
                            0.75,
                            "OFFER_STANDARD_RATES"));

        } else if (ficoScore >= 580) {
            recommendations.add(
                    new FinancialRecommendation(
                            "FAIR_CREDIT",
                            "Fair credit profile. Higher rates and additional scrutiny recommended.",
                            0.82,
                            "APPLY_HIGHER_RATES"));

        } else {
            recommendations.add(
                    new FinancialRecommendation(
                            "POOR_CREDIT",
                            String.format("Poor credit score of %d. High-risk lending considerations apply.", ficoScore),
                            0.90,
                            "CONSIDER_ALTERNATIVE_PRODUCTS"));
        }

        return recommendations;
    }

    private List<FinancialRecommendation> generateInterestRateRecommendations(
            double interestRate, double defaultProbability) {
        List<FinancialRecommendation> recommendations = new ArrayList<>();

        if (interestRate > 20) {
            recommendations.add(
                    new FinancialRecommendation(
                            "VERY_HIGH_RATE",
                            String.format("Interest rate of %.2f%% is very high. Verify applicant understands commitment.", 
                                    interestRate),
                            0.70,
                            "REQUIRE_RATE_ACKNOWLEDGMENT"));

        } else if (interestRate < 5) {
            recommendations.add(
                    new FinancialRecommendation(
                            "COMPETITIVE_RATE",
                            String.format("Interest rate of %.2f%% is competitive and favorable.", interestRate),
                            0.60,
                            "HIGHLIGHT_FAVORABLE_RATE"));
        }

        return recommendations;
    }

    private List<FinancialRecommendation> generateTermRecommendations(
            int term, double loanAmount, double interestRate) {
        List<FinancialRecommendation> recommendations = new ArrayList<>();

        double monthlyPayment = calculateMonthlyPayment(loanAmount, interestRate, term);

        if (term == 60) {
            recommendations.add(
                    new FinancialRecommendation(
                            "LONG_TERM_OPTION",
                            String.format("60-month term results in $%.2f monthly payment. Consider 36-month alternative for faster payoff.",
                                    monthlyPayment),
                            0.60,
                            "OFFER_SHORTER_TERM_OPTION"));

        } else if (term == 36) {
            recommendations.add(
                    new FinancialRecommendation(
                            "SHORT_TERM_OPTION",
                            String.format("36-month term results in $%.2f monthly payment. Faster payoff saves on interest.",
                                    monthlyPayment),
                            0.55,
                            "HIGHLIGHT_SAVINGS"));
        }

        return recommendations;
    }

    private double calculateMonthlyPayment(double principal, double annualRate, int months) {
        double monthlyRate = annualRate / 100 / 12;
        if (monthlyRate == 0) {
            return principal / months;
        }
        return principal
                * (monthlyRate * Math.pow(1 + monthlyRate, months))
                / (Math.pow(1 + monthlyRate, months) - 1);
    }
}
