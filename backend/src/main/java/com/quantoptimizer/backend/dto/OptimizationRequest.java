package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;

public class OptimizationRequest extends MarketDataRequest {

    private String objective = "max_sharpe";

    @Pattern(
            regexp = "random_search|scipy_max_sharpe|black_litterman",
            message = "optimizer must be random_search, scipy_max_sharpe, or black_litterman"
    )
    private String optimizer = "scipy_max_sharpe";

    @JsonAlias("riskFreeRate")
    @JsonProperty("risk_free_rate")
    private double riskFreeRate = 0.04;

    @DecimalMin(value = "0.0", inclusive = false)
    @DecimalMax("1.0")
    @JsonAlias("maxWeight")
    @JsonProperty("max_weight")
    private double maxWeight = 0.60;

    @Positive
    private int trials = 50_000;

    private int seed = 42;

    public String getObjective() {
        return objective;
    }

    public void setObjective(String objective) {
        this.objective = objective;
    }

    public String getOptimizer() {
        return optimizer;
    }

    public void setOptimizer(String optimizer) {
        this.optimizer = optimizer;
    }

    public double getRiskFreeRate() {
        return riskFreeRate;
    }

    public void setRiskFreeRate(double riskFreeRate) {
        this.riskFreeRate = riskFreeRate;
    }

    public double getMaxWeight() {
        return maxWeight;
    }

    public void setMaxWeight(double maxWeight) {
        this.maxWeight = maxWeight;
    }

    public int getTrials() {
        return trials;
    }

    public void setTrials(int trials) {
        this.trials = trials;
    }

    public int getSeed() {
        return seed;
    }

    public void setSeed(int seed) {
        this.seed = seed;
    }
}
