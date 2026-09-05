package com.akahalu.portfolio.presentation.skills

import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class SkillsViewModel(
    private val repository: PortfolioRepository,
    private val scope: CoroutineScope,
) {
    private val _uiState = MutableStateFlow<SkillsUiState>(
        SkillsUiState.Loading,
    )

    val uiState: StateFlow<SkillsUiState> = _uiState.asStateFlow()

    fun loadTechnologies() {
        scope.launch {
            _uiState.value = SkillsUiState.Loading

            runCatching {
                repository.getTechnologies()
            }.onSuccess { technologies ->
                _uiState.value = SkillsUiState.Success(
                    technologies = technologies,
                )
            }.onFailure { throwable ->
                _uiState.value = SkillsUiState.Error(
                    message = throwable.message
                        ?: "Unable to load skills and technologies.",
                )
            }
        }
    }
}