package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Positive;

public class FrontierRequest extends MarketDataRequest {

    @JsonAlias("riskFreeRate")
    @JsonProperty("risk_free_rate")
    private double riskFreeRate = RequestDefaults.DEFAULT_RISK_FREE_RATE;

    @DecimalMin(value = "0.0", inclusive = false)
    @DecimalMax("1.0")
    @JsonAlias("maxWeight")
    @JsonProperty("max_weight")
    private double maxWeight = RequestDefaults.DEFAULT_MAX_WEIGHT;

    @Min(2)
    private int points = RequestDefaults.DEFAULT_FRONTIER_POINTS;

    @Positive
    private int trials = RequestDefaults.DEFAULT_FRONTIER_TRIALS;

    private int seed = RequestDefaults.DEFAULT_SEED;

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

    public int getPoints() {
        return points;
    }

    public void setPoints(int points) {
        this.points = points;
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
