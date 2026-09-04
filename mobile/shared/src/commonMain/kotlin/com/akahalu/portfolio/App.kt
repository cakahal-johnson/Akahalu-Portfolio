package com.akahalu.portfolio

import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import com.akahalu.portfolio.core.di.PortfolioDependencies
import com.akahalu.portfolio.core.designsystem.theme.AkahaluPortfolioTheme
import com.akahalu.portfolio.core.navigation.AppDestination
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.presentation.home.HomeScreen
import com.akahalu.portfolio.presentation.portfolio.PortfolioViewModel
import com.akahalu.portfolio.presentation.projects.ProjectDetailScreen
import com.akahalu.portfolio.presentation.projects.ProjectDetailViewModel
import com.akahalu.portfolio.presentation.projects.ProjectsScreen

@Composable
fun App(
    networkConfig: NetworkConfig,
) {
    AkahaluPortfolioTheme {
        val dependencies = remember(networkConfig) {
            PortfolioDependencies(networkConfig)
        }

        DisposableEffect(dependencies) {
            onDispose {
                dependencies.httpClient.close()
            }
        }

        val scope = rememberCoroutineScope()

        val portfolioViewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            PortfolioViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val portfolioUiState by portfolioViewModel.uiState.collectAsState()

        var destination by remember {
            mutableStateOf<AppDestination>(
                AppDestination.Home,
            )
        }

        LaunchedEffect(portfolioViewModel) {
            portfolioViewModel.loadPortfolio()
        }

        when (val currentDestination = destination) {
            AppDestination.Home -> {
                HomeScreen(
                    uiState = portfolioUiState,
                    onProjectSelected = { slug ->
                        destination = AppDestination.ProjectDetail(slug)
                    },
                )
            }

            AppDestination.Projects -> {
                ProjectsScreen(
                    uiState = portfolioUiState,
                    onProjectSelected = { slug ->
                        destination = AppDestination.ProjectDetail(slug)
                    },
                )
            }

            is AppDestination.ProjectDetail -> {
                ProjectDetailRoute(
                    slug = currentDestination.slug,
                    repository = dependencies.portfolioRepository,
                    scope = scope,
                    onBack = {
                        destination = AppDestination.Projects
                    },
                )
            }

            AppDestination.Experience -> {
                Text(
                    text = "Experience",
                )
            }

            AppDestination.Contact -> {
                Text(
                    text = "Contact",
                )
            }
        }
    }
}

@Composable
private fun ProjectDetailRoute(
    slug: String,
    repository: com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository,
    scope: kotlinx.coroutines.CoroutineScope,
    onBack: () -> Unit,
) {
    val viewModel = remember(
        repository,
        scope,
        slug,
    ) {
        ProjectDetailViewModel(
            repository = repository,
            scope = scope,
        )
    }

    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(viewModel, slug) {
        viewModel.loadProject(slug)
    }

    ProjectDetailScreen(
        uiState = uiState,
        onBack = onBack,
    )
}