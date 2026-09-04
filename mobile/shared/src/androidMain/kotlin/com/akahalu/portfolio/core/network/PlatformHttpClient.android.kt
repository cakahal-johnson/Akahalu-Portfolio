package com.akahalu.portfolio.core.network

import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO

actual fun createPlatformHttpClient(
    config: NetworkConfig,
): HttpClient {
    return HttpClient(CIO) {
        configureCommonHttpClient(config)
    }
}