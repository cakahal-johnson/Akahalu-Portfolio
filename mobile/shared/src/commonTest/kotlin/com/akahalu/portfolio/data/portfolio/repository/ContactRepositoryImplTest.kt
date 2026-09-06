package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.core.network.ApiClient
import com.akahalu.portfolio.data.portfolio.remote.PortfolioRemoteDataSource
import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType
import io.ktor.client.HttpClient
import io.ktor.client.engine.mock.MockEngine
import io.ktor.client.engine.mock.MockEngineConfig
import io.ktor.client.engine.mock.respond
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.http.ContentType
import io.ktor.http.HttpMethod
import io.ktor.http.HttpStatusCode
import io.ktor.http.headersOf
import io.ktor.serialization.kotlinx.json.json
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class ContactRepositoryImplTest {

    @Test
    fun submitContactInquiryPostsAndMapsResponse() = runTest {
        var requestMethod: HttpMethod? = null

        val engine = MockEngine(
            MockEngineConfig().apply {
                requestHandlers.add { request ->
                    requestMethod = request.method

                    respond(
                        content = """{"message":"Your message has been received successfully."}""",
                        status = HttpStatusCode.OK,
                        headers = headersOf(
                            "Content-Type",
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
                        explicitNulls = false
                    },
                )
            }
        }

        val repository = PortfolioRepositoryImpl(
            PortfolioRemoteDataSource(
                ApiClient(httpClient),
            ),
        )

        val result = repository.submitContactInquiry(
            ContactInquirySubmission(
                name = "Akahalu Johnson",
                email = "contact@example.com",
                phone = "+1 306 555 0100",
                company = "Akahalu Technologies",
                subject = "Software development opportunity",
                message = "I would like to discuss a software development opportunity.",
                inquiryType = ContactInquiryType.EMPLOYMENT,
                consentGiven = true,
                sourcePage = "mobile/contact",
            ),
        )

        assertEquals(
            HttpMethod.Post,
            requestMethod,
        )

        assertEquals(
            "Your message has been received successfully.",
            result.message,
        )

        httpClient.close()
    }
}