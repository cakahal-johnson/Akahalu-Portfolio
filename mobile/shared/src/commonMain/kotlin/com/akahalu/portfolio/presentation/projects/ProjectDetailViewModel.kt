package com.akahalu.portfolio.presentation.projects

import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ProjectDetailViewModel(
    private val repository: PortfolioRepository,
    private val scope: CoroutineScope,
) {

    private val _uiState = MutableStateFlow<ProjectDetailUiState>(
        ProjectDetailUiState.Loading,
    )

    val uiState: StateFlow<ProjectDetailUiState> = _uiState.asStateFlow()

    fun loadProject(
        slug: String,
    ) {
        scope.launch {
            _uiState.value = ProjectDetailUiState.Loading

            runCatching {
                require(slug.isNotBlank()) {
                    "Project slug must not be blank."
                }

                repository.getProject(slug)
            }.onSuccess { project ->
                _uiState.value = ProjectDetailUiState.Success(
                    project = project,
                )
            }.onFailure { throwable ->
                _uiState.value = ProjectDetailUiState.Error(
                    message = throwable.message
                        ?: "Unable to load project.",
                )
            }
        }
    }
}