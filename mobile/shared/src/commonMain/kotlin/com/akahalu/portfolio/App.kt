package com.akahalu.portfolio

import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.collectAsState
import com.akahalu.portfolio.core.di.PortfolioDependencies
import com.akahalu.portfolio.core.designsystem.theme.AkahaluPortfolioTheme
import com.akahalu.portfolio.core.navigation.AppDestination
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.presentation.home.HomeScreen
import com.akahalu.portfolio.presentation.portfolio.PortfolioViewModel
import com.akahalu.portfolio.presentation.projects.ProjectDetailScreen
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

        val viewModel = remember(
            dependencies.portfolioRepository,
            scope,
        ) {
            PortfolioViewModel(
                repository = dependencies.portfolioRepository,
                scope = scope,
            )
        }

        val uiState by viewModel.uiState.collectAsState()

        var destination by remember {
            mutableStateOf<AppDestination>(
                AppDestination.Home,
            )
        }

        androidx.compose.runtime.LaunchedEffect(viewModel) {
            viewModel.loadPortfolio()
        }

        when (val currentDestination = destination) {
            AppDestination.Home -> {
                HomeScreen(
                    uiState = uiState,
                    onProjectSelected = { slug ->
                        destination = AppDestination.ProjectDetail(slug)
                    },
                )
            }

            AppDestination.Projects -> {
                ProjectsScreen(
                    uiState = uiState,
                    onProjectSelected = { slug ->
                        destination = AppDestination.ProjectDetail(slug)
                    },
                )
            }

            is AppDestination.ProjectDetail -> {
                val project = when (val state = uiState) {
                    is com.akahalu.portfolio.presentation.portfolio.PortfolioUiState.Success ->
                        state.projectPage.items.firstOrNull {
                            it.slug == currentDestination.slug
                        }

                    else -> null
                }

                if (project != null) {
                    ProjectDetailScreen(
                        project = project,
                    )
                } else {
                    androidx.compose.material3.Text(
                        text = "Project not found.",
                    )
                }
            }

            AppDestination.Experience -> {
                androidx.compose.material3.Text(
                    text = "Experience",
                )
            }

            AppDestination.Contact -> {
                androidx.compose.material3.Text(
                    text = "Contact",
                )
            }
        }
    }
}