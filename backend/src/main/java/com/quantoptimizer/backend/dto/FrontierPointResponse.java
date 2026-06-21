package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Map;

public record FrontierPointResponse(
        @JsonProperty("target_return")
        double targetReturn,
        @JsonProperty("expected_return")
        double expectedReturn,
        double volatility,
        @JsonProperty("sharpe_ratio")
        double sharpeRatio,
        Map<String, Double> weights
) {
}

