package com.akahalu.portfolio.presentation.projects

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.components.SkeletonBox
import com.akahalu.portfolio.presentation.components.SkeletonText

@Composable
fun ProjectDetailScreen(
    uiState: ProjectDetailUiState,
    onBack: () -> Unit,
    modifier: Modifier = Modifier,
) {
    AnimatedContent(
        targetState = uiState,
        modifier = modifier.fillMaxSize(),
        transitionSpec = {
            fadeIn() togetherWith fadeOut()
        },
        label = "project-detail-content",
    ) { state ->
        when (state) {
            ProjectDetailUiState.Loading -> {
                ProjectDetailLoading()
            }

            is ProjectDetailUiState.Error -> {
                ProjectDetailError(
                    message = state.message,
                    onBack = onBack,
                )
            }

            is ProjectDetailUiState.Success -> {
                ProjectDetailContent(
                    project = state.project,
                    onBack = onBack,
                )
            }
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
            .verticalScroll(
                rememberScrollState(),
            )
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        SkeletonBox(
            modifier = Modifier.size(
                width = 92.dp,
                height = 40.dp,
            ),
        )

        SkeletonText(
            width = 260.dp,
            height = 32.dp,
        )

        SkeletonText(
            width = null,
            height = 18.dp,
        )

        SkeletonText(
            width = null,
            height = 18.dp,
        )

        SkeletonText(
            width = 120.dp,
            height = 16.dp,
        )

        ProjectMediaLoading()

        repeat(4) {
            ProjectDetailSectionSkeleton()
        }
    }
}

@Composable
private fun ProjectMediaLoading(
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        SkeletonText(
            width = 120.dp,
            height = 20.dp,
        )

        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
            contentPadding = PaddingValues(
                vertical = AkahaluSpacing.Small,
            ),
        ) {
            items(3) {
                SkeletonBox(
                    modifier = Modifier.size(
                        width = 280.dp,
                        height = 190.dp,
                    ),
                    shape = MaterialTheme.shapes.large,
                )
            }
        }
    }
}

@Composable
private fun ProjectDetailSectionSkeleton() {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        SkeletonText(
            width = 130.dp,
            height = 20.dp,
        )

        SkeletonBox(
            modifier = Modifier
                .fillMaxWidth()
                .height(18.dp),
        )

        SkeletonBox(
            modifier = Modifier
                .fillMaxWidth()
                .height(18.dp),
        )

        SkeletonText(
            width = null,
            height = 18.dp,
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

        ProjectMediaGallery(
            media = project.media,
        )

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