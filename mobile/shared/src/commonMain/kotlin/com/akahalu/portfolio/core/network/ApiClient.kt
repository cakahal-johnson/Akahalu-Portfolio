package com.akahalu.portfolio.core.network

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.request.HttpRequestBuilder
import io.ktor.client.request.get

class ApiClient(
    @PublishedApi
    internal val httpClient: HttpClient,
) {

    suspend inline fun <reified T> get(
        path: String,
        crossinline block: HttpRequestBuilder.() -> Unit = {},
    ): T {
        return try {
            httpClient.get(path) {
                block()
            }.body()
        } catch (exception: NetworkException) {
            throw exception
        } catch (exception: Exception) {
            throw NetworkException.RequestFailed(
                message = exception.message
                    ?: "Network request failed.",
                cause = exception,
            )
        }
    }
}