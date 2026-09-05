package com.akahalu.portfolio.presentation.contact

import com.akahalu.portfolio.domain.portfolio.model.Profile

sealed interface ContactUiState {

    data object Loading : ContactUiState

    data class Success(
        val profile: Profile,
    ) : ContactUiState

    data class Error(
        val message: String,
    ) : ContactUiState
}
