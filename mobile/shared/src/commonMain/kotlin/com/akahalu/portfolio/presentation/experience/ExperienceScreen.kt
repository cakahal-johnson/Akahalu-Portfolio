package com.akahalu.portfolio.presentation.experience

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.SubcomposeAsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.core.platform.ExternalUrlLauncher
import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText

@Composable
fun ExperienceScreen(
    uiState: ExperienceUiState,
    externalUrlLauncher: ExternalUrlLauncher,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier,
) {
    when (uiState) {
        ExperienceUiState.Loading -> {
            ExperienceLoading(
                modifier = modifier,
            )
        }

        is ExperienceUiState.Error -> {
            ExperienceError(
                message = uiState.message,
                onRetry = onRetry,
                modifier = modifier,
            )
        }

        is ExperienceUiState.Success -> {
            if (uiState.experiences.isEmpty()) {
                ExperienceEmpty(
                    modifier = modifier,
                )
            } else {
                ExperienceContent(
                    experiences = uiState.experiences,
                    externalUrlLauncher = externalUrlLauncher,
                    modifier = modifier,
                )
            }
        }
    }
}

@Composable
private fun ExperienceContent(
    experiences: List<Experience>,
    externalUrlLauncher: ExternalUrlLauncher,
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        contentPadding = PaddingValues(
            horizontal = AkahaluSpacing.Large,
            vertical = AkahaluSpacing.Large,
        ),
    ) {
        item {
            Column(
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Experience",
                    style = MaterialTheme.typography.headlineMedium,
                )

                Text(
                    text = "A summary of my professional journey, roles, and the work I have contributed to.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }

        itemsIndexed(
            items = experiences,
            key = { _, experience ->
                experience.id
            },
        ) { index, experience ->
            ExperienceTimelineItem(
                experience = experience,
                isLast = index == experiences.lastIndex,
                externalUrlLauncher = externalUrlLauncher,
            )
        }
    }
}

@Composable
private fun ExperienceTimelineItem(
    experience: Experience,
    isLast: Boolean,
    externalUrlLauncher: ExternalUrlLauncher,
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .height(IntrinsicSize.Min),
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        verticalAlignment = Alignment.Top,
    ) {
        ExperienceTimelineRail(
            isLast = isLast,
        )

        ExperienceCard(
            experience = experience,
            externalUrlLauncher = externalUrlLauncher,
            modifier = Modifier.weight(1f),
        )
    }
}

@Composable
private fun ExperienceTimelineRail(
    isLast: Boolean,
) {
    Column(
        modifier = Modifier
            .width(12.dp)
            .fillMaxHeight(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            modifier = Modifier
                .size(12.dp)
                .clip(CircleShape)
                .background(
                    MaterialTheme.colorScheme.primary,
                ),
        )

        if (!isLast) {
            Box(
                modifier = Modifier
                    .width(2.dp)
                    .weight(1f)
                    .background(
                        MaterialTheme.colorScheme.outlineVariant,
                    ),
            )
        }
    }
}

@Composable
private fun ExperienceCard(
    experience: Experience,
    externalUrlLauncher: ExternalUrlLauncher,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.large,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface,
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 2.dp,
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
            ExperienceHeader(
                experience = experience,
            )

            ExperienceMeta(
                experience = experience,
            )

            if (experience.summary.isNotBlank()) {
                Text(
                    text = experience.summary,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurface,
                )
            }

            experience.responsibilities
                ?.takeIf { it.isNotBlank() }
                ?.let { responsibilities ->
                    ExperienceSection(
                        title = "Responsibilities",
                        content = responsibilities,
                    )
                }

            experience.achievements
                ?.takeIf { it.isNotBlank() }
                ?.let { achievements ->
                    ExperienceSection(
                        title = "Achievements",
                        content = achievements,
                    )
                }

            experience.companyWebsite
                ?.takeIf { it.isNotBlank() }
                ?.let { website ->
                    TextButton(
                        onClick = {
                            externalUrlLauncher.openUrl(website)
                        },
                    ) {
                        Text(
                            text = "Visit company website",
                        )
                    }
                }
        }
    }
}

@Composable
private fun ExperienceHeader(
    experience: Experience,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = experience.jobTitle,
            style = MaterialTheme.typography.titleLarge,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            experience.companyLogoUrl
                ?.takeIf { it.isNotBlank() }
                ?.let { logoUrl ->
                    CompanyLogo(
                        url = logoUrl,
                        companyName = experience.companyName,
                    )
                }

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.ExtraSmall,
                ),
            ) {
                Text(
                    text = experience.companyName,
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.primary,
                )

                if (experience.isCurrent) {
                    StatusBadge(
                        text = "Current",
                        emphasized = true,
                    )
                }
            }
        }
    }
}

@Composable
private fun CompanyLogo(
    url: String,
    companyName: String,
) {
    SubcomposeAsyncImage(
        model = url,
        contentDescription = "$companyName logo",
        modifier = Modifier
            .size(56.dp)
            .clip(MaterialTheme.shapes.medium),
        contentScale = ContentScale.Crop,
        loading = {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        MaterialTheme.colorScheme.surfaceVariant,
                    ),
            )
        },
        error = {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(
                        MaterialTheme.colorScheme.primaryContainer,
                    ),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    text = companyInitials(companyName),
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                )
            }
        },
    )
}

@Composable
private fun ExperienceMeta(
    experience: Experience,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = formatDateRange(experience),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            MetaBadge(
                text = formatEmploymentType(
                    experience.employmentType,
                ),
                modifier = Modifier.weight(1f),
            )

            MetaBadge(
                text = formatLocation(experience),
                modifier = Modifier.weight(1f),
            )
        }

        if (experience.isFeatured) {
            Row(
                modifier = Modifier.fillMaxWidth(),
            ) {
                StatusBadge(
                    text = "Featured",
                    emphasized = false,
                )
            }
        }
    }
}

@Composable
private fun MetaBadge(
    text: String,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(8.dp),
        color = MaterialTheme.colorScheme.surfaceVariant,
    ) {
        Text(
            text = text,
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 10.dp,
                    vertical = 6.dp,
                ),
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun StatusBadge(
    text: String,
    emphasized: Boolean,
) {
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = if (emphasized) {
            MaterialTheme.colorScheme.primaryContainer
        } else {
            MaterialTheme.colorScheme.secondaryContainer
        },
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(
                horizontal = 8.dp,
                vertical = 5.dp,
            ),
            style = MaterialTheme.typography.labelSmall,
            color = if (emphasized) {
                MaterialTheme.colorScheme.onPrimaryContainer
            } else {
                MaterialTheme.colorScheme.onSecondaryContainer
            },
        )
    }
}

@Composable
private fun ExperienceSection(
    title: String,
    content: String,
) {
    val bulletItems = content
        .lines()
        .map { line ->
            line
                .trim()
                .removePrefix("•")
                .removePrefix("-")
                .trim()
        }
        .filter { it.isNotBlank() }

    if (bulletItems.isEmpty()) {
        return
    }

    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.primary,
        )

        Column(
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            bulletItems.forEach { item ->
                ExperienceBulletPoint(
                    text = item,
                )
            }
        }
    }
}

@Composable
private fun ExperienceBulletPoint(
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
private fun ExperienceLoading(
    modifier: Modifier = Modifier,
) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        contentPadding = PaddingValues(
            horizontal = AkahaluSpacing.Large,
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
                    width = 140.dp,
                    height = 32.dp,
                )

                SkeletonText(
                    width = null,
                    height = 18.dp,
                )
            }
        }

        items(4) {
            SkeletonCard()
        }
    }
}

@Composable
private fun ExperienceError(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "Unable to load experience",
            style = MaterialTheme.typography.titleMedium,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Text(
            text = message,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.error,
        )

        TextButton(
            onClick = onRetry,
        ) {
            Text(text = "Retry")
        }
    }
}

@Composable
private fun ExperienceEmpty(
    modifier: Modifier = Modifier,
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(AkahaluSpacing.Large),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "No experience available",
            style = MaterialTheme.typography.titleMedium,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Text(
            text = "Professional experience will appear here once it has been added.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

private fun companyInitials(
    companyName: String,
): String {
    val words = companyName
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

        else -> "CO"
    }
}

private fun formatDateRange(
    experience: Experience,
): String {
    val end = if (experience.isCurrent) {
        "Present"
    } else {
        experience.endDate ?: "Present"
    }

    return "${experience.startDate} - $end"
}

private fun formatEmploymentType(
    employmentType: EmploymentType,
): String {
    return when (employmentType) {
        EmploymentType.FULL_TIME -> "Full-time"
        EmploymentType.PART_TIME -> "Part-time"
        EmploymentType.CONTRACT -> "Contract"
        EmploymentType.FREELANCE -> "Freelance"
        EmploymentType.INTERNSHIP -> "Internship"
        EmploymentType.APPRENTICESHIP -> "Apprenticeship"
        EmploymentType.TEMPORARY -> "Temporary"
        EmploymentType.VOLUNTEER -> "Volunteer"
        EmploymentType.SELF_EMPLOYED -> "Self-employed"
        EmploymentType.OTHER -> "Other"
    }
}

private fun formatLocation(
    experience: Experience,
): String {
    val type = when (experience.locationType) {
        ExperienceLocationType.ONSITE -> "On-site"
        ExperienceLocationType.REMOTE -> "Remote"
        ExperienceLocationType.HYBRID -> "Hybrid"
    }

    return experience.location
        ?.takeIf { it.isNotBlank() }
        ?.let { "$type · $it" }
        ?: type
}