package com.financialadvisor.engine;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * JVM entrypoint for the finance recommendation engine.
 * 
 * Runs as a Spring Boot REST API service on port 8080
 */
@SpringBootApplication
public class EngineApplication {

    public static void main(String[] args) {
        SpringApplication.run(EngineApplication.class, args);
    }
}
