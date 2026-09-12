package com.akahalu.portfolio.presentation.projects

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState
import kotlinx.coroutines.delay

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
            horizontal = AkahaluSpacing.Medium,
            vertical = AkahaluSpacing.Large,
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
                    height = 32.dp,
                )

                SkeletonText(
                    width = 280.dp,
                    height = 18.dp,
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
    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        contentAlignment = Alignment.Center,
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceContainer,
            ),
        ) {
            Column(
                modifier = Modifier.padding(
                    AkahaluSpacing.Large,
                ),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Unable to load projects",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.error,
                )
            }
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
            horizontal = AkahaluSpacing.Medium,
            vertical = AkahaluSpacing.Large,
        ),
    ) {
        item {
            ProjectsHeader(
                projectCount = projects.size,
            )
        }

        items(
            items = projects,
            key = { project -> project.id },
        ) { project ->
            AnimatedProjectCard(
                project = project,
                onClick = {
                    onProjectSelected(project.slug)
                },
            )
        }
    }
}

@Composable
private fun ProjectsHeader(
    projectCount: Int,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Projects",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = "A selection of applications, platforms, and technical work I have built.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Text(
            text = "$projectCount project${if (projectCount == 1) "" else "s"}",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun AnimatedProjectCard(
    project: Project,
    onClick: () -> Unit,
) {
    var visible by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(project.id) {
        delay(80)
        visible = true
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(),
    ) {
        ProjectCard(
            project = project,
            onClick = onClick,
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
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainer,
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 2.dp,
        ),
    ) {
        Column {
            ProjectThumbnail(
                project = project,
            )

            Column(
                modifier = Modifier.padding(
                    AkahaluSpacing.Medium,
                ),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                ProjectCardBadges(
                    project = project,
                )

                Text(
                    text = project.title,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = project.shortDescription,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )

                if (project.technologies.isNotEmpty()) {
                    ProjectTechnologyRow(
                        project = project,
                    )
                }

                ProjectDate(
                    project = project,
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.End,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        text = "View project →",
                        style = MaterialTheme.typography.labelLarge,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.SemiBold,
                    )
                }
            }
        }
    }
}

@Composable
private fun ProjectThumbnail(
    project: Project,
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(190.dp)
            .background(
                MaterialTheme.colorScheme.surfaceVariant,
            ),
        contentAlignment = Alignment.Center,
    ) {
        if (!project.thumbnailUrl.isNullOrBlank()) {
            AsyncImage(
                model = project.thumbnailUrl,
                contentDescription = "${project.title} project preview",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        } else {
            ProjectThumbnailFallback(
                title = project.title,
            )
        }

        if (project.isFeatured) {
            Surface(
                modifier = Modifier
                    .align(Alignment.TopEnd)
                    .padding(AkahaluSpacing.Medium),
                shape = RoundedCornerShape(50),
                color = MaterialTheme.colorScheme.primaryContainer,
            ) {
                Text(
                    text = "Featured",
                    modifier = Modifier.padding(
                        horizontal = 10.dp,
                        vertical = 6.dp,
                    ),
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
    }
}

@Composable
private fun ProjectThumbnailFallback(
    title: String,
) {
    Box(
        modifier = Modifier
            .size(72.dp)
            .clip(CircleShape)
            .background(
                MaterialTheme.colorScheme.primaryContainer,
            ),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = projectInitials(title),
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
        )
    }
}

@Composable
private fun ProjectCardBadges(
    project: Project,
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        project.category
            ?.name
            ?.takeIf { it.isNotBlank() }
            ?.let { category ->
                ProjectBadge(
                    text = category,
                    emphasized = true,
                )
            }

        if (project.status == ProjectStatus.PUBLISHED) {
            ProjectBadge(
                text = "Published",
                emphasized = false,
            )
        }
    }
}

@Composable
private fun ProjectTechnologyRow(
    project: Project,
) {
    Row(
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        project.technologies
            .take(3)
            .forEach { technology ->
                Surface(
                    shape = RoundedCornerShape(50),
                    color = MaterialTheme.colorScheme.secondaryContainer,
                ) {
                    Text(
                        text = technology.name,
                        modifier = Modifier.padding(
                            horizontal = 10.dp,
                            vertical = 5.dp,
                        ),
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSecondaryContainer,
                    )
                }
            }

        if (project.technologies.size > 3) {
            Surface(
                shape = RoundedCornerShape(50),
                color = MaterialTheme.colorScheme.surfaceVariant,
            ) {
                Text(
                    text = "+${project.technologies.size - 3}",
                    modifier = Modifier.padding(
                        horizontal = 10.dp,
                        vertical = 5.dp,
                    ),
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun ProjectDate(
    project: Project,
) {
    val date = when {
        !project.publishedAt.isNullOrBlank() ->
            project.publishedAt

        !project.completedAt.isNullOrBlank() ->
            project.completedAt

        !project.startedAt.isNullOrBlank() ->
            project.startedAt

        else -> null
    }

    date?.let {
        Text(
            text = formatProjectDate(it),
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProjectEmptyState(
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        contentAlignment = Alignment.Center,
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
        ) {
            Column(
                modifier = Modifier.padding(
                    AkahaluSpacing.Large,
                ),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "No projects available",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )

                Text(
                    text = "There are currently no portfolio projects to display.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

private fun projectInitials(
    title: String,
): String {
    val words = title
        .trim()
        .split(Regex("\\s+"))
        .filter { it.isNotBlank() }

    return when {
        words.size >= 2 -> {
            words
                .take(2)
                .joinToString("") { word ->
                    word.first().uppercase()
                }
        }

        words.size == 1 -> {
            words.first()
                .take(2)
                .uppercase()
        }

        else -> "PR"
    }
}

private fun formatProjectDate(
    value: String,
): String {
    return value
        .take(10)
        .replace("-", " / ")
}