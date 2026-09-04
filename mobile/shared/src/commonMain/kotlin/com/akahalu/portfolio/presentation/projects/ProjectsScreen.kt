package com.akahalu.portfolio.presentation.projects

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
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState

@Composable
fun ProjectsScreen(
    uiState: PortfolioUiState,
    onProjectSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    when (uiState) {
        PortfolioUiState.Loading -> {
            Text(
                text = "Loading projects...",
                modifier = modifier.padding(AkahaluSpacing.Large),
            )
        }

        is PortfolioUiState.Error -> {
            Text(
                text = uiState.message,
                modifier = modifier.padding(AkahaluSpacing.Large),
                color = MaterialTheme.colorScheme.error,
            )
        }

        is PortfolioUiState.Success -> {
            ProjectList(
                projects = uiState.projectPage.items,
                onProjectSelected = onProjectSelected,
                modifier = modifier,
            )
        }
    }
}

@Composable
private fun ProjectList(
    projects: List<Project>,
    onProjectSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    if (projects.isEmpty()) {
        Text(
            text = "No projects available.",
            modifier = modifier.padding(AkahaluSpacing.Large),
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
private fun ProjectCard(
    project: Project,
    onClick: () -> Unit,
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
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