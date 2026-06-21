package com.quantoptimizer.backend;

import com.quantoptimizer.backend.config.QuantEngineProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties(QuantEngineProperties.class)
public class QuantOptimizerBackendApplication {

    public static void main(String[] args) {
        SpringApplication.run(QuantOptimizerBackendApplication.class, args);
    }
}

