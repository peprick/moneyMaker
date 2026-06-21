package com.quantoptimizer.backend.dto;

public record HealthResponse(String backend, QuantEngineHealthResponse quantEngine) {
}

