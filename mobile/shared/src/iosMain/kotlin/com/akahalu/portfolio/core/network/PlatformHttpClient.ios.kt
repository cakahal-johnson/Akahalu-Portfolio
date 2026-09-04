package com.akahalu.portfolio.core.network

import io.ktor.client.HttpClient
import io.ktor.client.engine.darwin.Darwin

actual fun createPlatformHttpClient(
    config: NetworkConfig,
): HttpClient {
    return HttpClient(Darwin) {
        configureCommonHttpClient(config)
    }
}