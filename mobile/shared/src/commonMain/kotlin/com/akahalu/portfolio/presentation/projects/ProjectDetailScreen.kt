package com.akahalu.portfolio.presentation.projects

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project

@Composable
fun ProjectDetailScreen(
    uiState: ProjectDetailUiState,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when (uiState) {
        ProjectDetailUiState.Loading -> {
            ProjectDetailLoading(
                modifier = modifier,
            )
        }

        is ProjectDetailUiState.Error -> {
            ProjectDetailError(
                message = uiState.message,
                onBack = onBack,
                modifier = modifier,
            )
        }

        is ProjectDetailUiState.Success -> {
            ProjectDetailContent(
                project = uiState.project,
                onBack = onBack,
                modifier = modifier,
            )
        }
    }
}

@Composable
private fun ProjectDetailLoading(
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        Text(
            text = "Loading project...",
            style = MaterialTheme.typography.bodyLarge,
        )
    }
}

@Composable
private fun ProjectDetailError(
    message: String,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        Text(
            text = "Unable to load project",
            style = MaterialTheme.typography.headlineSmall,
        )

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.error,
        )

        Button(
            onClick = onBack,
        ) {
            Text(
                text = "Back to projects",
            )
        }
    }
}

@Composable
private fun ProjectDetailContent(
    project: Project,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(
                rememberScrollState(),
            )
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        Button(
            onClick = onBack,
        ) {
            Text(
                text = "Back",
            )
        }

        Text(
            text = project.title,
            style = MaterialTheme.typography.headlineMedium,
        )

        Text(
            text = project.shortDescription,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        project.category?.let { category ->
            Text(
                text = "Category: ${category.name}",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
            )
        }

        project.description?.let { description ->
            DetailSection(
                title = "Overview",
                content = description,
            )
        }

        project.problemStatement?.let { problem ->
            DetailSection(
                title = "Problem",
                content = problem,
            )
        }

        project.solutionSummary?.let { solution ->
            DetailSection(
                title = "Solution",
                content = solution,
            )
        }

        project.keyFeatures?.let { features ->
            DetailSection(
                title = "Key Features",
                content = features,
            )
        }

        project.technicalHighlights?.let { highlights ->
            DetailSection(
                title = "Technical Highlights",
                content = highlights,
            )
        }

        if (project.technologies.isNotEmpty()) {
            DetailSection(
                title = "Technologies",
                content = project.technologies.joinToString(", ") {
                    it.name
                },
            )
        }

        project.repositoryUrl?.let { repositoryUrl ->
            DetailSection(
                title = "Repository",
                content = repositoryUrl,
            )
        }

        project.liveUrl?.let { liveUrl ->
            DetailSection(
                title = "Live Project",
                content = liveUrl,
            )
        }

        project.caseStudyUrl?.let { caseStudyUrl ->
            DetailSection(
                title = "Case Study",
                content = caseStudyUrl,
            )
        }
    }
}

@Composable
private fun DetailSection(
    title: String,
    content: String,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleMedium,
        )

        Text(
            text = content,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}