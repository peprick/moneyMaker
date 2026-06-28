package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Positive;

public class OptimizationRequest extends MarketDataRequest {

    private String objective = RequestDefaults.DEFAULT_OBJECTIVE;

    @Pattern(
            regexp = RequestDefaults.OPTIMIZER_PATTERN,
            message = RequestDefaults.OPTIMIZER_MESSAGE
    )
    private String optimizer = RequestDefaults.DEFAULT_OPTIMIZER;

    @JsonAlias("riskFreeRate")
    @JsonProperty("risk_free_rate")
    private double riskFreeRate = RequestDefaults.DEFAULT_RISK_FREE_RATE;

    @DecimalMin(value = "0.0", inclusive = false)
    @DecimalMax("1.0")
    @JsonAlias("maxWeight")
    @JsonProperty("max_weight")
    private double maxWeight = RequestDefaults.DEFAULT_MAX_WEIGHT;

    @Positive
    private int trials = RequestDefaults.DEFAULT_OPTIMIZER_TRIALS;

    private int seed = RequestDefaults.DEFAULT_SEED;

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
