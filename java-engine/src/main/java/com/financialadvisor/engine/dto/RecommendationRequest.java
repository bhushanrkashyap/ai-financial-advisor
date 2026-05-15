package com.financialadvisor.engine.dto;

import java.io.Serializable;

/**
 * Request DTO for recommendation generation.
 * Contains loan application data and prediction results.
 */
public class RecommendationRequest implements Serializable {

    private double loanAmount;
    private int term;
    private double interestRate;
    private double defaultProbability;
    private String riskLevel;
    private int ficoScore;
    private double dtiRatio;
    private double annualIncome;

    // Getters and Setters
    public double getLoanAmount() {
        return loanAmount;
    }

    public void setLoanAmount(double loanAmount) {
        this.loanAmount = loanAmount;
    }

    public int getTerm() {
        return term;
    }

    public void setTerm(int term) {
        this.term = term;
    }

    public double getInterestRate() {
        return interestRate;
    }

    public void setInterestRate(double interestRate) {
        this.interestRate = interestRate;
    }

    public double getDefaultProbability() {
        return defaultProbability;
    }

    public void setDefaultProbability(double defaultProbability) {
        this.defaultProbability = defaultProbability;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public int getFicoScore() {
        return ficoScore;
    }

    public void setFicoScore(int ficoScore) {
        this.ficoScore = ficoScore;
    }

    public double getDtiRatio() {
        return dtiRatio;
    }

    public void setDtiRatio(double dtiRatio) {
        this.dtiRatio = dtiRatio;
    }

    public double getAnnualIncome() {
        return annualIncome;
    }

    public void setAnnualIncome(double annualIncome) {
        this.annualIncome = annualIncome;
    }
}
