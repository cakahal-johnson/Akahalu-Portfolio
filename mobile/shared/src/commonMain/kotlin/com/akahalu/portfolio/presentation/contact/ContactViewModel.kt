package com.akahalu.portfolio.presentation.contact

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
}
