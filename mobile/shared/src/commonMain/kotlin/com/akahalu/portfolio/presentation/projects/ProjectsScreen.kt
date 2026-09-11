package com.akahalu.portfolio.presentation.projects

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState

@Composable
fun ProjectsScreen(
    uiState: PortfolioUiState,
    onProjectSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    AnimatedContent(
        targetState = uiState,
        modifier = modifier.fillMaxSize(),
        transitionSpec = {
            fadeIn() togetherWith fadeOut()
        },
        label = "projects-content",
    ) { state ->
        when (state) {
            PortfolioUiState.Loading -> {
                ProjectsLoading()
            }

            is PortfolioUiState.Error -> {
                ProjectsError(
                    message = state.message,
                )
            }

            is PortfolioUiState.Success -> {
                ProjectList(
                    projects = state.projectPage.items,
                    onProjectSelected = onProjectSelected,
                )
            }
        }
    }
}

@Composable
private fun ProjectsLoading(
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        contentPadding = PaddingValues(
            AkahaluSpacing.Large,
        ),
    ) {
        item {
            Column(
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                SkeletonText(
                    width = 150.dp,
                    height = 28.dp,
                )

                SkeletonText(
                    width = 240.dp,
                    height = 16.dp,
                )
            }
        }

        items(
            count = 6,
        ) {
            SkeletonCard()
        }
    }
}

@Composable
private fun ProjectsError(
    message: String,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Unable to load projects",
            style = MaterialTheme.typography.headlineSmall,
        )

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.error,
        )
    }
}

@Composable
private fun ProjectList(
    projects: List<Project>,
    onProjectSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    if (projects.isEmpty()) {
        ProjectEmptyState(
            modifier = modifier,
        )
        return
    }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        contentPadding = PaddingValues(
            AkahaluSpacing.Large,
        ),
    ) {
        items(
            items = projects,
            key = { project -> project.id },
        ) { project ->
            ProjectCard(
                project = project,
                onClick = {
                    onProjectSelected(project.slug)
                },
            )
        }
    }
}

@Composable
private fun ProjectEmptyState(
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "No projects available",
            style = MaterialTheme.typography.headlineSmall,
        )

        Text(
            text = "There are currently no portfolio projects to display.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProjectCard(
    project: Project,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        shape = MaterialTheme.shapes.medium,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            Text(
                text = project.title,
                style = MaterialTheme.typography.titleLarge,
            )

            Text(
                text = project.shortDescription,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            project.category?.let { category ->
                Text(
                    text = category.name,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}