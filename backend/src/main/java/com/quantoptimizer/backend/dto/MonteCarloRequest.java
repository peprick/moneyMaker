package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Positive;

public class MonteCarloRequest extends WeightedMarketDataRequest {

    @Positive
    private int days = RequestDefaults.DEFAULT_MONTE_CARLO_DAYS;

    @Positive
    private int simulations = RequestDefaults.DEFAULT_MONTE_CARLO_SIMULATIONS;

    @Positive
    @JsonAlias("initialValue")
    @JsonProperty("initial_value")
    private double initialValue = RequestDefaults.DEFAULT_INITIAL_VALUE;

    private int seed = RequestDefaults.DEFAULT_SEED;

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
