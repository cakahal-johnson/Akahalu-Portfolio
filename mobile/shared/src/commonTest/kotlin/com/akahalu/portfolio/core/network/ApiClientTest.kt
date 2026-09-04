package com.akahalu.portfolio.core.network

import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.MockEngineConfig
import io.ktor.client.engine.mock.respond
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class ApiClientTest {

    @Test
    fun clientCanDecodeJsonResponse() = runTest {
        val engine = MockEngine(
            MockEngineConfig().apply {
                requestHandlers.add {
                    respond(
                        content = """{"message":"ok"}""",
                        status = HttpStatusCode.OK,
                        headers = headersOf(
                            HttpHeaders.ContentType,
                            ContentType.Application.Json.toString(),
                        ),
                    )
                }
            },
        )

        val httpClient = HttpClient(engine) {
            install(ContentNegotiation) {
                json(
                    Json {
                        ignoreUnknownKeys = true
                    },
                )
            }
        }

        val apiClient = ApiClient(httpClient)

        val response: TestResponse = apiClient.get("/health")

        assertEquals(
            "ok",
            response.message,
        )

        httpClient.close()
    }

    @Serializable
    private data class TestResponse(
        val message: String,
    )
}