package com.quantoptimizer.backend.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class RestClientConfig {

    @Bean
    RestClient quantEngineRestClient(RestClient.Builder builder, QuantEngineProperties properties) {
        return builder.baseUrl(properties.getBaseUrl()).build();
    }
}

