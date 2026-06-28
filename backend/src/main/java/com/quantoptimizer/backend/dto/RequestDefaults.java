package com.quantoptimizer.backend.dto;

public final class RequestDefaults {

    public static final String DEFAULT_OBJECTIVE = "max_sharpe";
    public static final String DEFAULT_OPTIMIZER = "hierarchical_risk_parity";
    public static final String OPTIMIZER_PATTERN =
            "hierarchical_risk_parity|random_search|scipy_max_sharpe|black_litterman";
    public static final String OPTIMIZER_MESSAGE =
            "optimizer must be hierarchical_risk_parity, random_search, scipy_max_sharpe, or black_litterman";

    public static final double DEFAULT_RISK_FREE_RATE = 0.04;
    public static final double DEFAULT_MAX_WEIGHT = 0.60;
    public static final int DEFAULT_OPTIMIZER_TRIALS = 50_000;
    public static final int DEFAULT_FRONTIER_POINTS = 12;
    public static final int DEFAULT_FRONTIER_TRIALS = 60_000;
    public static final int DEFAULT_MONTE_CARLO_DAYS = 252;
    public static final int DEFAULT_MONTE_CARLO_SIMULATIONS = 1_000;
    public static final double DEFAULT_INITIAL_VALUE = 100_000.0;
    public static final int DEFAULT_SEED = 42;

    private RequestDefaults() {
    }
}
