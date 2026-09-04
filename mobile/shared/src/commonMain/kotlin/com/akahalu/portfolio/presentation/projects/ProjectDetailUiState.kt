package com.akahalu.portfolio.presentation.projects

import com.akahalu.portfolio.domain.portfolio.model.Project

sealed interface ProjectDetailUiState {

    data object Loading : ProjectDetailUiState

    data class Success(
        val project: Project,
    ) : ProjectDetailUiState

    data class Error(
        val message: String,
    ) : ProjectDetailUiState
}