package com.akahalu.portfolio.data.portfolio.dto

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ContactInquiryCreateDto(
    val name: String,
    val email: String,
    val phone: String? = null,
    val company: String? = null,
    val subject: String,
    val message: String,
    @SerialName("inquiry_type")
    val inquiryType: String = "general",
    @SerialName("project_id")
    val projectId: String? = null,
    @SerialName("consent_given")
    val consentGiven: Boolean = false,
    @SerialName("source_page")
    val sourcePage: String? = "mobile/contact",
    val website: String? = null,
)

@Serializable
data class ContactInquiryResponseDto(
    val message: String,
)