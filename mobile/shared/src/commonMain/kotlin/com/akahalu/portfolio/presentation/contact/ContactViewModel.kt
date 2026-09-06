package com.akahalu.portfolio.presentation.contact

import com.akahalu.portfolio.domain.portfolio.model.ContactInquirySubmission
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ContactViewModel(
    private val repository: PortfolioRepository,
    private val scope: CoroutineScope,
) {

    private val _uiState = MutableStateFlow<ContactUiState>(
        ContactUiState.Loading,
    )

    val uiState: StateFlow<ContactUiState> =
        _uiState.asStateFlow()

    fun loadProfile() {
        scope.launch {
            _uiState.value = ContactUiState.Loading

            runCatching {
                repository.getProfile()
            }.onSuccess { profile ->
                _uiState.value = ContactUiState.Success(
                    profile = profile,
                )
            }.onFailure { throwable ->
                _uiState.value = ContactUiState.Error(
                    message = throwable.message
                        ?: "Unable to load contact information.",
                )
            }
        }
    }

    fun updateName(value: String) {
        updateForm { copy(name = value, validationError = null) }
    }

    fun updateEmail(value: String) {
        updateForm { copy(email = value, validationError = null) }
    }

    fun updatePhone(value: String) {
        updateForm { copy(phone = value, validationError = null) }
    }

    fun updateCompany(value: String) {
        updateForm { copy(company = value, validationError = null) }
    }

    fun updateInquiryType(value: com.akahalu.portfolio.domain.portfolio.model.ContactInquiryType) {
        updateForm {
            copy(
                inquiryType = value,
                validationError = null,
            )
        }
    }

    fun updateSubject(value: String) {
        updateForm { copy(subject = value, validationError = null) }
    }

    fun updateMessage(value: String) {
        updateForm { copy(message = value, validationError = null) }
    }

    fun updateConsentGiven(value: Boolean) {
        updateForm {
            copy(
                consentGiven = value,
                validationError = null,
            )
        }
    }

    fun submitContactInquiry() {
        val currentState = _uiState.value

        if (currentState !is ContactUiState.Success) {
            return
        }

        val form = currentState.form

        val validationError = validate(form)

        if (validationError != null) {
            _uiState.value = currentState.copy(
                form = form.copy(
                    validationError = validationError,
                ),
            )
            return
        }

        scope.launch {
            _uiState.value = currentState.copy(
                form = form.copy(
                    isSubmitting = true,
                    submissionMessage = null,
                    submissionError = null,
                    validationError = null,
                ),
            )

            val submission = ContactInquirySubmission(
                name = form.name.trim(),
                email = form.email.trim(),
                phone = form.phone.trim().ifBlank { null },
                company = form.company.trim().ifBlank { null },
                subject = form.subject.trim(),
                message = form.message.trim(),
                inquiryType = form.inquiryType,
                projectId = null,
                consentGiven = form.consentGiven,
                sourcePage = "mobile/contact",
            )

            runCatching {
                repository.submitContactInquiry(submission)
            }.onSuccess { result ->
                _uiState.value = currentState.copy(
                    form = form.copy(
                        isSubmitting = false,
                        submissionMessage = result.message,
                        submissionError = null,
                        validationError = null,
                    ),
                )
            }.onFailure { throwable ->
                _uiState.value = currentState.copy(
                    form = form.copy(
                        isSubmitting = false,
                        submissionMessage = null,
                        submissionError = throwable.message
                            ?: "Unable to send your message.",
                    ),
                )
            }
        }
    }

    private fun updateForm(
        transform: ContactFormState.() -> ContactFormState,
    ) {
        val currentState = _uiState.value

        if (currentState is ContactUiState.Success) {
            _uiState.value = currentState.copy(
                form = currentState.form.transform(),
            )
        }
    }

    private fun validate(
        form: ContactFormState,
    ): String? {
        if (form.name.trim().length < 2) {
            return "Please enter your name."
        }

        if (!EMAIL_PATTERN.matches(form.email.trim())) {
            return "Please enter a valid email address."
        }

        if (form.subject.trim().length < 3) {
            return "Please enter a subject."
        }

        if (form.message.trim().length < 10) {
            return "Please enter at least 10 characters in your message."
        }

        return null
    }

    private companion object {
        val EMAIL_PATTERN =
            Regex("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")
    }
}