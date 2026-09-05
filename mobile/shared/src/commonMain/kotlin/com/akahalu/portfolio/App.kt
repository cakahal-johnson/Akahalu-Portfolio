package com.akahalu.portfolio

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.di.PortfolioDependencies
import com.akahalu.portfolio.core.designsystem.theme.AkahaluPortfolioTheme
import com.akahalu.portfolio.core.navigation.AppDestination
import com.akahalu.portfolio.core.navigation.AppNavigator
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.domain.portfolio.repository.PortfolioRepository
import com.akahalu.portfolio.presentation.home.HomeScreen
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState
import com.akahalu.portfolio.presentation.portfolio.PortfolioViewModel
import com.akahalu.portfolio.presentation.projects.ProjectDetailScreen
import com.akahalu.portfolio.presentation.projects.ProjectDetailViewModel
import com.akahalu.portfolio.presentation.projects.ProjectsScreen
import com.akahalu.portfolio.presentation.shell.AppNavigationBar
import com.akahalu.portfolio.presentation.shell.PlaceholderScreen
import kotlinx.coroutines.CoroutineScope

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

        val navigator = remember {
            AppNavigator()
        }

        val currentDestination by navigator.currentDestination
            .collectAsState()

        LaunchedEffect(portfolioViewModel) {
            portfolioViewModel.loadPortfolio()
        }

        AppContent(
            destination = currentDestination,
            portfolioUiState = portfolioUiState,
            portfolioRepository = dependencies.portfolioRepository,
            scope = scope,
            onTopLevelDestinationSelected = {
                navigator.navigateToTopLevel(it)
            },
            onProjectSelected = { slug ->
                navigator.navigateToProjectDetail(slug)
            },
            onBackFromProjectDetail = {
                navigator.goBack()
            },
        )
    }
}

@Composable
private fun AppContent(
    destination: AppDestination,
    portfolioUiState: PortfolioUiState,
    portfolioRepository: PortfolioRepository,
    scope: CoroutineScope,
    onTopLevelDestinationSelected: (AppDestination) -> Unit,
    onProjectSelected: (String) -> Unit,
    onBackFromProjectDetail: () -> Unit,
) {
    val isDetailDestination =
        destination is AppDestination.ProjectDetail

    Scaffold(
        bottomBar = {
            if (!isDetailDestination) {
                AppNavigationBar(
                    currentDestination = destination,
                    onDestinationSelected = onTopLevelDestinationSelected,
                )
            }
        },
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
        ) {
            when (destination) {
                AppDestination.Home -> {
                    HomeScreen(
                        uiState = portfolioUiState,
                        onProjectSelected = onProjectSelected,
                    )
                }

                AppDestination.Projects -> {
                    ProjectsScreen(
                        uiState = portfolioUiState,
                        onProjectSelected = onProjectSelected,
                    )
                }

                is AppDestination.ProjectDetail -> {
                    ProjectDetailRoute(
                        slug = destination.slug,
                        repository = portfolioRepository,
                        scope = scope,
                        onBack = onBackFromProjectDetail,
                    )
                }

                AppDestination.Experience -> {
                    PlaceholderScreen(
                        title = "Experience",
                        subtitle =
                            "Professional experience will be added in a future milestone.",
                    )
                }

                AppDestination.Contact -> {
                    PlaceholderScreen(
                        title = "Contact",
                        subtitle =
                            "Contact functionality will be added in a future milestone.",
                    )
                }
            }
        }
    }
}

@Composable
private fun ProjectDetailRoute(
    slug: String,
    repository: PortfolioRepository,
    scope: CoroutineScope,
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