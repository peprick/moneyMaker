package com.quantoptimizer.backend.controller;

import com.quantoptimizer.backend.dto.FrontierRequest;
import com.quantoptimizer.backend.dto.FrontierResponse;
import com.quantoptimizer.backend.dto.HealthResponse;
import com.quantoptimizer.backend.dto.MonteCarloRequest;
import com.quantoptimizer.backend.dto.MonteCarloResponse;
import com.quantoptimizer.backend.dto.OptimizationRequest;
import com.quantoptimizer.backend.dto.OptimizationResponse;
import com.quantoptimizer.backend.dto.RiskRequest;
import com.quantoptimizer.backend.dto.RiskResponse;
import com.quantoptimizer.backend.service.QuantEngineClient;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class QuantController {

    private final QuantEngineClient quantEngineClient;

    public QuantController(QuantEngineClient quantEngineClient) {
        this.quantEngineClient = quantEngineClient;
    }

    @GetMapping("/health")
    public HealthResponse health() {
        return new HealthResponse("ok", quantEngineClient.health());
    }

    @PostMapping("/optimize")
    public OptimizationResponse optimize(@Valid @RequestBody OptimizationRequest request) {
        return quantEngineClient.optimize(request);
    }

    @PostMapping("/risk")
    public RiskResponse risk(@Valid @RequestBody RiskRequest request) {
        return quantEngineClient.risk(request);
    }

    @PostMapping("/frontier")
    public FrontierResponse frontier(@Valid @RequestBody FrontierRequest request) {
        return quantEngineClient.frontier(request);
    }

    @PostMapping("/montecarlo")
    public MonteCarloResponse monteCarlo(@Valid @RequestBody MonteCarloRequest request) {
        return quantEngineClient.monteCarlo(request);
    }
}
