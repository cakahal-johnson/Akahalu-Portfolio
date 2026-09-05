package com.akahalu.portfolio.presentation.experience

import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ExperienceViewModel(
    private val repository: PortfolioRepository,
    private val scope: CoroutineScope,
) {
    private val _uiState =
        MutableStateFlow<ExperienceUiState>(
            ExperienceUiState.Loading,
        )

    val uiState: StateFlow<ExperienceUiState> =
        _uiState.asStateFlow()

    fun loadExperiences() {
        scope.launch {
            _uiState.value =
                ExperienceUiState.Loading

            runCatching {
                repository.getExperiences()
            }.onSuccess { page ->
                _uiState.value =
                    ExperienceUiState.Success(
                        experiences = page.items,
                    )
            }.onFailure { throwable ->
                _uiState.value =
                    ExperienceUiState.Error(
                        message =
                            throwable.message
                                ?: "Unable to load experience.",
                    )
            }
        }
    }
}