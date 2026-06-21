package com.quantoptimizer.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record MonteCarloResponse(
        List<Double> p10,
        List<Double> p25,
        List<Double> p50,
        List<Double> p75,
        List<Double> p90,
        @JsonProperty("final_p10")
        double finalP10,
        @JsonProperty("final_p50")
        double finalP50,
        @JsonProperty("final_p90")
        double finalP90
) {
}

