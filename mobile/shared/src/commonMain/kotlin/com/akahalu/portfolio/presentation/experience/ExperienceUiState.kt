package com.akahalu.portfolio.presentation.experience

import com.akahalu.portfolio.domain.portfolio.model.Experience

sealed interface ExperienceUiState {

    data object Loading : ExperienceUiState

    data class Success(
        val experiences: List<Experience>,
    ) : ExperienceUiState

    data class Error(
        val message: String,
    ) : ExperienceUiState
}