package com.akahalu.portfolio.presentation.portfolio

import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectPage

sealed interface PortfolioUiState {

    data object Loading : PortfolioUiState

    data class Success(
        val featuredProjects: List<Project>,
        val projectPage: ProjectPage,
    ) : PortfolioUiState

    data class Error(
        val message: String,
    ) : PortfolioUiState
}