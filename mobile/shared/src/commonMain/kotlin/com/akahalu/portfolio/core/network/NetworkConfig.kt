package com.akahalu.portfolio.core.network

data class NetworkConfig(
    val baseUrl: String,
    val connectTimeoutMillis: Long = 15_000,
    val requestTimeoutMillis: Long = 30_000,
    val socketTimeoutMillis: Long = 30_000,
) {
    init {
        require(baseUrl.isNotBlank()) {
            "Network base URL must not be blank."
        }

        require(baseUrl.endsWith("/")) {
            "Network base URL must end with '/'."
        }
    }

    companion object {
        const val API_V1_PATH = "api/v1"
    }
}