package com.akahalu.portfolio.presentation.skills

import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology

sealed interface SkillsUiState {
    data object Loading : SkillsUiState

    data class Success(
        val technologies: List<ProjectTechnology>,
    ) : SkillsUiState

    data class Error(
        val message: String,
    ) : SkillsUiState
}