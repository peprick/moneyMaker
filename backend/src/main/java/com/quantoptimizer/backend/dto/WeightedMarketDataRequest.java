package com.quantoptimizer.backend.dto;

import jakarta.validation.constraints.NotEmpty;
import java.util.Map;

public class WeightedMarketDataRequest extends MarketDataRequest {

    @NotEmpty
    private Map<String, Double> weights;

    public Map<String, Double> getWeights() {
        return weights;
    }

    public void setWeights(Map<String, Double> weights) {
        this.weights = weights;
    }
}

