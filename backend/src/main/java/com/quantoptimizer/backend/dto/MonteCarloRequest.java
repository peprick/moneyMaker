package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Positive;

public class MonteCarloRequest extends WeightedMarketDataRequest {

    @Positive
    private int days = 252;

    @Positive
    private int simulations = 1_000;

    @Positive
    @JsonAlias("initialValue")
    @JsonProperty("initial_value")
    private double initialValue = 100_000.0;

    private int seed = 42;

    public int getDays() {
        return days;
    }

    public void setDays(int days) {
        this.days = days;
    }

    public int getSimulations() {
        return simulations;
    }

    public void setSimulations(int simulations) {
        this.simulations = simulations;
    }

    public double getInitialValue() {
        return initialValue;
    }

    public void setInitialValue(double initialValue) {
        this.initialValue = initialValue;
    }

    public int getSeed() {
        return seed;
    }

    public void setSeed(int seed) {
        this.seed = seed;
    }
}

