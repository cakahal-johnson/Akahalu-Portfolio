package com.akahalu.portfolio.presentation.projects

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.core.platform.ExternalUrlLauncher
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.domain.portfolio.model.ProjectLink
import com.akahalu.portfolio.domain.portfolio.model.ProjectLinkType
import com.akahalu.portfolio.domain.portfolio.model.ProjectStatus
import com.akahalu.portfolio.presentation.components.SkeletonBox
import com.akahalu.portfolio.presentation.components.SkeletonText

@Composable
fun ProjectDetailScreen(
    uiState: ProjectDetailUiState,
    onBack: () -> Unit,
    externalUrlLauncher: ExternalUrlLauncher,
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
                    externalUrlLauncher = externalUrlLauncher,
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
            .padding(AkahaluSpacing.Medium),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        SkeletonBox(
            modifier = Modifier.size(
                width = 110.dp,
                height = 40.dp,
            ),
        )

        SkeletonBox(
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp),
            shape = MaterialTheme.shapes.large,
        )

        SkeletonText(
            width = 280.dp,
            height = 34.dp,
        )

        SkeletonText(
            width = null,
            height = 18.dp,
        )

        SkeletonText(
            width = null,
            height = 18.dp,
        )

        ProjectDetailSectionSkeleton()

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
            width = 130.dp,
            height = 22.dp,
        )

        androidx.compose.foundation.lazy.LazyRow(
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
            height = 22.dp,
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
                    AkahaluSpacing.Medium,
                ),
            ) {
                Text(
                    text = "Unable to load project",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
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
    }
}

@Composable
private fun ProjectDetailContent(
    project: Project,
    onBack: () -> Unit,
    externalUrlLauncher: ExternalUrlLauncher,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(
                rememberScrollState(),
            )
            .padding(
                horizontal = AkahaluSpacing.Medium,
                vertical = AkahaluSpacing.Large,
            ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
    ) {
        TextButton(
            onClick = onBack,
        ) {
            Text(
                text = "← Back to projects",
            )
        }

        ProjectHero(
            project = project,
        )

        ProjectMetadata(
            project = project,
        )

        if (project.technologies.isNotEmpty()) {
            ProjectTechnologySection(
                project = project,
            )
        }

        ProjectMediaGallery(
            media = project.media,
        )

        project.description
            ?.takeIf { it.isNotBlank() }
            ?.let { description ->
                DetailSection(
                    title = "Overview",
                    content = description,
                )
            }

        project.problemStatement
            ?.takeIf { it.isNotBlank() }
            ?.let { problem ->
                DetailSection(
                    title = "The problem",
                    content = problem,
                )
            }

        project.solutionSummary
            ?.takeIf { it.isNotBlank() }
            ?.let { solution ->
                DetailSection(
                    title = "The solution",
                    content = solution,
                )
            }

        project.keyFeatures
            ?.takeIf { it.isNotBlank() }
            ?.let { features ->
                BulletDetailSection(
                    title = "Key features",
                    content = features,
                )
            }

        project.technicalHighlights
            ?.takeIf { it.isNotBlank() }
            ?.let { highlights ->
                BulletDetailSection(
                    title = "Technical highlights",
                    content = highlights,
                )
            }

        ProjectLinksSection(
            project = project,
            externalUrlLauncher = externalUrlLauncher,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Medium,
            ),
        )
    }
}

@Composable
private fun ProjectHero(
    project: Project,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(230.dp)
                .clip(MaterialTheme.shapes.large)
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
                ProjectHeroFallback(
                    title = project.title,
                )
            }
        }

        ProjectHeroBadges(
            project = project,
        )

        Text(
            text = project.title,
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = project.shortDescription,
            style = MaterialTheme.typography.bodyLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProjectHeroFallback(
    title: String,
) {
    Box(
        modifier = Modifier
            .size(96.dp)
            .clip(CircleShape)
            .background(
                MaterialTheme.colorScheme.primaryContainer,
            ),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = projectInitials(title),
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
        )
    }
}

@Composable
private fun ProjectHeroBadges(
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

        if (project.isFeatured) {
            ProjectBadge(
                text = "Featured",
                emphasized = false,
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
private fun ProjectMetadata(
    project: Project,
) {
    val dates = buildList {
        project.startedAt
            ?.takeIf { it.isNotBlank() }
            ?.let { start ->
                add("Started ${formatProjectDate(start)}")
            }

        project.completedAt
            ?.takeIf { it.isNotBlank() }
            ?.let { completed ->
                add("Completed ${formatProjectDate(completed)}")
            }

        project.publishedAt
            ?.takeIf { it.isNotBlank() }
            ?.let { published ->
                add("Published ${formatProjectDate(published)}")
            }
    }

    if (dates.isEmpty()) {
        return
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainer,
        ),
    ) {
        Column(
            modifier = Modifier.padding(
                AkahaluSpacing.Medium,
            ),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            dates.forEach { date ->
                Text(
                    text = date,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun ProjectTechnologySection(
    project: Project,
) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Technologies",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
        )

        Column(
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            project.technologies.chunked(3).forEach { rowItems ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(
                        AkahaluSpacing.Small,
                    ),
                ) {
                    rowItems.forEach { technology ->
                        Surface(
                            modifier = Modifier.weight(1f),
                            shape = RoundedCornerShape(50),
                            color = MaterialTheme.colorScheme.secondaryContainer,
                        ) {
                            Text(
                                text = technology.name,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(
                                        horizontal = 10.dp,
                                        vertical = 7.dp,
                                    ),
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.onSecondaryContainer,
                            )
                        }
                    }

                    repeat(3 - rowItems.size) {
                        Spacer(
                            modifier = Modifier.weight(1f),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailSection(
    title: String,
    content: String,
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
                text = title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = content,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface,
            )
        }
    }
}

@Composable
private fun BulletDetailSection(
    title: String,
    content: String,
) {
    val items = parseBulletItems(content)

    if (items.isEmpty()) {
        return
    }

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
                AkahaluSpacing.Medium,
            ),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )

            Column(
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                items.forEach { item ->
                    BulletPoint(
                        text = item,
                    )
                }
            }
        }
    }
}

@Composable
private fun BulletPoint(
    text: String,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            modifier = Modifier
                .padding(top = 7.dp)
                .size(6.dp)
                .clip(CircleShape)
                .background(
                    MaterialTheme.colorScheme.primary,
                ),
        )

        Text(
            text = text,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface,
        )
    }
}

@Composable
private fun ProjectLinksSection(
    project: Project,
    externalUrlLauncher: ExternalUrlLauncher,
) {
    val links = buildProjectLinks(project)

    if (links.isEmpty()) {
        return
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer,
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
                text = "Project links",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )

            links.forEach { link ->
                OutlinedButton(
                    onClick = {
                        externalUrlLauncher.openUrl(link.url)
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(
                        text = link.label,
                    )
                }
            }
        }
    }
}

private data class DisplayProjectLink(
    val label: String,
    val url: String,
)

private fun buildProjectLinks(
    project: Project,
): List<DisplayProjectLink> {
    val links = mutableListOf<DisplayProjectLink>()

    project.repositoryUrl
        ?.takeIf { it.isNotBlank() }
        ?.let { url ->
            links.add(
                DisplayProjectLink(
                    label = "View repository",
                    url = url,
                ),
            )
        }

    project.liveUrl
        ?.takeIf { it.isNotBlank() }
        ?.let { url ->
            links.add(
                DisplayProjectLink(
                    label = "View live project",
                    url = url,
                ),
            )
        }

    project.caseStudyUrl
        ?.takeIf { it.isNotBlank() }
        ?.let { url ->
            links.add(
                DisplayProjectLink(
                    label = "Read case study",
                    url = url,
                ),
            )
        }

    project.links
        .sortedBy { it.sortOrder }
        .forEach { link ->
            if (
                links.none { existing ->
                    existing.url == link.url
                }
            ) {
                links.add(
                    DisplayProjectLink(
                        label = linkDisplayLabel(link),
                        url = link.url,
                    ),
                )
            }
        }

    return links
}

private fun linkDisplayLabel(
    link: ProjectLink,
): String {
    if (link.label.isNotBlank()) {
        return link.label
    }

    return when (link.linkType) {
        ProjectLinkType.REPOSITORY ->
            "View repository"

        ProjectLinkType.LIVE_DEMO ->
            "View live demo"

        ProjectLinkType.DOCUMENTATION ->
            "View documentation"

        ProjectLinkType.CASE_STUDY ->
            "Read case study"

        ProjectLinkType.VIDEO ->
            "Watch video"

        ProjectLinkType.DOWNLOAD ->
            "Download"

        ProjectLinkType.APP_STORE ->
            "Open App Store"

        ProjectLinkType.PLAY_STORE ->
            "Open Google Play"

        ProjectLinkType.DESIGN ->
            "View design"

        ProjectLinkType.ARTICLE ->
            "Read article"

        ProjectLinkType.API ->
            "View API"

        ProjectLinkType.OTHER ->
            "Open link"
    }
}

private fun parseBulletItems(
    content: String,
): List<String> {
    val lines = content.lines()

    val parsed = lines
        .map { line ->
            line
                .trim()
                .removePrefix("•")
                .removePrefix("-")
                .removePrefix("*")
                .trim()
        }
        .filter { it.isNotBlank() }

    if (parsed.isNotEmpty()) {
        return parsed
    }

    return content
        .split(".")
        .map { it.trim() }
        .filter { it.isNotBlank() }
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