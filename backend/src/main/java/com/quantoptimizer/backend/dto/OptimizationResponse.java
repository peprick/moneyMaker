package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public record OptimizationResponse(
        Map<String, Double> weights,
        @JsonProperty("expected_return")
        double expectedReturn,
        double volatility,
        @JsonProperty("sharpe_ratio")
        double sharpeRatio,
        @JsonProperty("price_rows")
        int priceRows,
        String start,
        String end
) {
}

