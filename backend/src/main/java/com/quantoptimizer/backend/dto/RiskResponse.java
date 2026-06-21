package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record RiskResponse(
        @JsonProperty("historical_var_95")
        double historicalVar95,
        @JsonProperty("parametric_var_95")
        double parametricVar95,
        @JsonProperty("max_drawdown")
        double maxDrawdown,
        @JsonProperty("annual_volatility")
        double annualVolatility,
        Double beta
) {
}

