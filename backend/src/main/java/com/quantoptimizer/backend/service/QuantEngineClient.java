package com.quantoptimizer.backend.service;

import com.quantoptimizer.backend.dto.FrontierRequest;
import com.quantoptimizer.backend.dto.FrontierResponse;
import com.quantoptimizer.backend.dto.MonteCarloRequest;
import com.quantoptimizer.backend.dto.MonteCarloResponse;
import com.quantoptimizer.backend.dto.OptimizationRequest;
import com.quantoptimizer.backend.dto.OptimizationResponse;
import com.quantoptimizer.backend.dto.QuantEngineHealthResponse;
import com.quantoptimizer.backend.dto.RiskRequest;
import com.quantoptimizer.backend.dto.RiskResponse;
import com.quantoptimizer.backend.exception.QuantEngineException;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

@Service
public class QuantEngineClient {

    private final RestClient quantEngineRestClient;

    public QuantEngineClient(RestClient quantEngineRestClient) {
        this.quantEngineRestClient = quantEngineRestClient;
    }

    public QuantEngineHealthResponse health() {
        return get("/health", QuantEngineHealthResponse.class);
    }

    public OptimizationResponse optimize(OptimizationRequest request) {
        return post("/optimize", request, OptimizationResponse.class);
    }

    public RiskResponse risk(RiskRequest request) {
        return post("/risk", request, RiskResponse.class);
    }

    public FrontierResponse frontier(FrontierRequest request) {
        return post("/frontier", request, FrontierResponse.class);
    }

    public MonteCarloResponse monteCarlo(MonteCarloRequest request) {
        return post("/montecarlo", request, MonteCarloResponse.class);
    }

    private <T> T get(String path, Class<T> responseType) {
        try {
            return quantEngineRestClient
                    .get()
                    .uri(path)
                    .retrieve()
                    .body(responseType);
        } catch (RestClientException exception) {
            throw new QuantEngineException("Python quant engine is unavailable: " + path, exception);
        }
    }

    private <T> T post(String path, Object request, Class<T> responseType) {
        try {
            return quantEngineRestClient
                    .post()
                    .uri(path)
                    .body(request)
                    .retrieve()
                    .body(responseType);
        } catch (RestClientException exception) {
            throw new QuantEngineException("Python quant engine request failed: " + path, exception);
        }
    }
}
