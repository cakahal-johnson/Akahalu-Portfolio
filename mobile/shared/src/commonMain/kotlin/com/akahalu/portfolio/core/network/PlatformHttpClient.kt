package com.akahalu.portfolio.core.network

import io.ktor.client.HttpClient
import io.ktor.client.HttpClientConfig
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.plugins.defaultRequest
import io.ktor.client.plugins.logging.LogLevel
import io.ktor.client.plugins.logging.Logger
import io.ktor.client.plugins.logging.Logging
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

expect fun createPlatformHttpClient(
    config: NetworkConfig,
): HttpClient

private object AkahaluHttpLogger : Logger {
    override fun log(message: String) {
        println(message)
    }
}

internal fun HttpClientConfig<*>.configureCommonHttpClient(
    config: NetworkConfig,
) {
    expectSuccess = true

    install(ContentNegotiation) {
        json(
            Json {
                ignoreUnknownKeys = true
                isLenient = false
                explicitNulls = false
                encodeDefaults = true
            },
        )
    }

    install(HttpTimeout) {
        connectTimeoutMillis = config.connectTimeoutMillis
        requestTimeoutMillis = config.requestTimeoutMillis
        socketTimeoutMillis = config.socketTimeoutMillis
    }

    install(Logging) {
        logger = AkahaluHttpLogger
        level = LogLevel.INFO
    }

    defaultRequest {
        url(config.baseUrl)
        contentType(ContentType.Application.Json)
    }
}