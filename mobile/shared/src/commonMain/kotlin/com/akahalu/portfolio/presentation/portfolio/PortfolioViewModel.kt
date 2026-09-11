package com.akahalu.portfolio.presentation.portfolio

import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class PortfolioViewModel(
    private val repository: PortfolioRepository,
    private val scope: CoroutineScope,
) {

    private val _uiState = MutableStateFlow<PortfolioUiState>(
        PortfolioUiState.Loading,
    )

    val uiState: StateFlow<PortfolioUiState> = _uiState.asStateFlow()

    fun loadPortfolio() {
        scope.launch {
            _uiState.value = PortfolioUiState.Loading

            runCatching {
                val profile = repository.getProfile()
                val featuredProjects = repository.getFeaturedProjects()
                val projectPage = repository.getProjects()

                PortfolioUiState.Success(
                    profile = profile,
                    featuredProjects = featuredProjects,
                    projectPage = projectPage,
                )
            }.onSuccess { state ->
                _uiState.value = state
            }.onFailure { throwable ->
                _uiState.value = PortfolioUiState.Error(
                    message = throwable.message
                        ?: "Unable to load portfolio data.",
                )
            }
        }
    }
}