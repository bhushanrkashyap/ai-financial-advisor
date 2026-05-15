package com.financialadvisor.engine.controller;

import com.financialadvisor.engine.dto.RecommendationRequest;
import com.financialadvisor.engine.dto.RecommendationResponse;
import com.financialadvisor.engine.recommendation.FinancialRecommendation;
import com.financialadvisor.engine.recommendation.IRecommendationEngine;
import com.financialadvisor.engine.recommendation.RecommendationEngine;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.logging.Logger;

/**
 * REST API Controller for the Financial Advisor Recommendation Engine.
 * Provides endpoints for generating recommendations based on loan data.
 */
@RestController
@RequestMapping("/api/engine")
@CrossOrigin(origins = "*", maxAge = 3600)
public class RecommendationController {

    private static final Logger logger = Logger.getLogger(RecommendationController.class.getName());
    private final IRecommendationEngine engine = new RecommendationEngine();

    /**
     * Health check endpoint.
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Java Recommendation Engine is running");
    }

    /**
     * Generate financial recommendations for a loan application.
     *
     * @param request Loan application data including prediction results
     * @return Recommendations with priority scores
     */
    @PostMapping("/recommend")
    public ResponseEntity<RecommendationResponse> generateRecommendations(
            @RequestBody RecommendationRequest request) {
        
        logger.info("Generating recommendations for loan: $" + request.getLoanAmount());

        // Generate recommendations from the engine
        List<FinancialRecommendation> recommendations = engine.generateRecommendations(
                request.getLoanAmount(),
                request.getInterestRate(),
                request.getTerm(),
                request.getDefaultProbability(),
                request.getRiskLevel(),
                request.getFicoScore(),
                request.getDtiRatio(),
                request.getAnnualIncome()
        );

        // Get additional analysis
        int optimalTerm = engine.getOptimalLoanTerm(
                request.getLoanAmount(),
                request.getFicoScore(),
                request.getDtiRatio()
        );

        double recommendedRate = engine.getRecommendedInterestRate(
                request.getInterestRate(),
                request.getDefaultProbability(),
                request.getFicoScore()
        );

        boolean shouldApprove = engine.shouldApproveLoan(
                request.getDefaultProbability(),
                request.getRiskLevel(),
                request.getDtiRatio()
        );

        // Build response
        RecommendationResponse response = new RecommendationResponse();
        response.setRecommendations(recommendations);
        response.setOptimalTerm(optimalTerm);
        response.setRecommendedInterestRate(recommendedRate);
        response.setShouldApprove(shouldApprove);
        response.setPrimaryRecommendation(getTopRecommendation(recommendations));

        return ResponseEntity.ok(response);
    }

    /**
     * Get the top priority recommendation.
     */
    private String getTopRecommendation(List<FinancialRecommendation> recommendations) {
        if (recommendations == null || recommendations.isEmpty()) {
            return "No specific recommendations available";
        }
        return recommendations.get(0).getDescription();
    }
}
