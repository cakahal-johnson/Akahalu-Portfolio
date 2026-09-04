package com.akahalu.portfolio.presentation.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState

@Composable
fun HomeScreen(
    uiState: PortfolioUiState,
    onProjectSelected: (String) -> Unit,
) {
    when (uiState) {
        PortfolioUiState.Loading -> {
            Text(
                text = "Loading portfolio…",
                modifier = androidx.compose.ui.Modifier.padding(
                    AkahaluSpacing.Large,
                ),
            )
        }

        is PortfolioUiState.Error -> {
            Text(
                text = uiState.message,
                modifier = androidx.compose.ui.Modifier.padding(
                    AkahaluSpacing.Large,
                ),
                color = MaterialTheme.colorScheme.error,
            )
        }

        is PortfolioUiState.Success -> {
            HomeContent(
                featuredProjects = uiState.featuredProjects,
                onProjectSelected = onProjectSelected,
            )
        }
    }
}

@Composable
private fun HomeContent(
    featuredProjects: List<Project>,
    onProjectSelected: (String) -> Unit,
) {
    LazyColumn(
        modifier = androidx.compose.ui.Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(
            AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        item {
            Column(
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Akahalu Portfolio",
                    style = MaterialTheme.typography.headlineMedium,
                )

                Text(
                    text = "Software Developer and Telecom Engineer",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                Text(
                    text = "Featured Projects",
                    modifier = androidx.compose.ui.Modifier.padding(
                        top = AkahaluSpacing.Medium,
                    ),
                    style = MaterialTheme.typography.titleLarge,
                )
            }
        }

        items(
            items = featuredProjects,
            key = { project -> project.id },
        ) { project ->
            Card(
                onClick = {
                    onProjectSelected(project.slug)
                },
            ) {
                Column(
                    modifier = androidx.compose.ui.Modifier.padding(
                        AkahaluSpacing.Large,
                    ),
                    verticalArrangement = Arrangement.spacedBy(
                        AkahaluSpacing.Small,
                    ),
                ) {
                    Text(
                        text = project.title,
                        style = MaterialTheme.typography.titleMedium,
                    )

                    Text(
                        text = project.shortDescription,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        }
    }
}