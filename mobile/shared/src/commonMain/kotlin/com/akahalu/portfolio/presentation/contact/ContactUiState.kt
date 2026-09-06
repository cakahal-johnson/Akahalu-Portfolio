package com.akahalu.portfolio.presentation.contact

import com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType
import com.akahalu.portfolio.domain.portfolio.model.Profile

data class ContactFormState(
    val name: String = "",
    val email: String = "",
    val phone: String = "",
    val company: String = "",
    val inquiryType: ContactInquiryType = ContactInquiryType.GENERAL,
    val subject: String = "",
    val message: String = "",
    val consentGiven: Boolean = false,
    val isSubmitting: Boolean = false,
    val submissionMessage: String? = null,
    val submissionError: String? = null,
    val validationError: String? = null,
)

sealed interface ContactUiState {

    data object Loading : ContactUiState

    data class Success(
        val profile: Profile,
        val form: ContactFormState = ContactFormState(),
    ) : ContactUiState

    data class Error(
        val message: String,
    ) : ContactUiState
}