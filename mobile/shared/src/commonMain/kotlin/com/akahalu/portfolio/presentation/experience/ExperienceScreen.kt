package com.akahalu.portfolio.presentation.experience

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
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
import coil3.compose.SubcomposeAsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.core.platform.ExternalUrlLauncher
import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import kotlinx.coroutines.delay

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
            horizontal = AkahaluSpacing.Medium,
            vertical = AkahaluSpacing.Large,
        ),
    ) {
        item {
            ExperienceHeader(
                experienceCount = experiences.size,
            )
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
private fun ExperienceHeader(
    experienceCount: Int,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Professional Experience",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = "A timeline of the roles, companies, and technical work that shaped my professional journey.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Text(
            text = "$experienceCount role${if (experienceCount == 1) "" else "s"}",
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun ExperienceTimelineItem(
    experience: Experience,
    isLast: Boolean,
    externalUrlLauncher: ExternalUrlLauncher,
) {
    var visible by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(experience.id) {
        delay(80)
        visible = true
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn() + slideInVertically(
            initialOffsetY = { 24 },
        ),
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
        shape = RoundedCornerShape(22.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceContainer,
        ),
        elevation = CardDefaults.cardElevation(
            defaultElevation = 2.dp,
        ),
    ) {
        Column(
            modifier = Modifier.padding(
                AkahaluSpacing.Medium,
            ),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            ExperienceCardHeader(
                experience = experience,
            )

            ExperienceMeta(
                experience = experience,
            )

            ExperienceDivider()

            if (experience.summary.isNotBlank()) {
                ExperienceSummary(
                    summary = experience.summary,
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
                    ExperienceWebsiteAction(
                        website = website,
                        externalUrlLauncher = externalUrlLauncher,
                    )
                }
        }
    }
}

@Composable
private fun ExperienceCardHeader(
    experience: Experience,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
        verticalAlignment = Alignment.Top,
    ) {
        experience.companyLogoUrl
            ?.takeIf { it.isNotBlank() }
            ?.let { logoUrl ->
                CompanyLogo(
                    url = logoUrl,
                    companyName = experience.companyName,
                )
            }
            ?: CompanyLogoFallback(
                companyName = experience.companyName,
            )

        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.ExtraSmall,
            ),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
                verticalAlignment = Alignment.Top,
            ) {
                Text(
                    text = experience.jobTitle,
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold,
                )

                if (experience.isFeatured) {
                    ExperienceBadge(
                        text = "Featured",
                        emphasized = false,
                    )
                }
            }

            Text(
                text = experience.companyName,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
            )

            if (experience.isCurrent) {
                ExperienceBadge(
                    text = "Current",
                    emphasized = true,
                )
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
            CompanyLogoFallbackContent(
                companyName = companyName,
            )
        },
    )
}

@Composable
private fun CompanyLogoFallback(
    companyName: String,
) {
    Box(
        modifier = Modifier
            .size(56.dp)
            .clip(MaterialTheme.shapes.medium),
        contentAlignment = Alignment.Center,
    ) {
        CompanyLogoFallbackContent(
            companyName = companyName,
        )
    }
}

@Composable
private fun CompanyLogoFallbackContent(
    companyName: String,
) {
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
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimaryContainer,
        )
    }
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
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            fontWeight = FontWeight.SemiBold,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            ExperienceMetaBadge(
                text = formatEmploymentType(
                    experience.employmentType,
                ),
                modifier = Modifier.weight(1f),
            )

            ExperienceMetaBadge(
                text = formatLocation(experience),
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun ExperienceMetaBadge(
    text: String,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(10.dp),
        color = MaterialTheme.colorScheme.secondaryContainer,
    ) {
        Text(
            text = text,
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = 10.dp,
                    vertical = 7.dp,
                ),
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSecondaryContainer,
            fontWeight = FontWeight.Medium,
        )
    }
}

@Composable
private fun ExperienceBadge(
    text: String,
    emphasized: Boolean,
) {
    Surface(
        shape = RoundedCornerShape(50),
        color = if (emphasized) {
            MaterialTheme.colorScheme.primaryContainer
        } else {
            MaterialTheme.colorScheme.surfaceVariant
        },
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(
                horizontal = 10.dp,
                vertical = 5.dp,
            ),
            style = MaterialTheme.typography.labelMedium,
            color = if (emphasized) {
                MaterialTheme.colorScheme.onPrimaryContainer
            } else {
                MaterialTheme.colorScheme.onSurfaceVariant
            },
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
private fun ExperienceDivider() {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(
                MaterialTheme.colorScheme.outlineVariant.copy(
                    alpha = 0.5f,
                ),
            ),
    )
}

@Composable
private fun ExperienceSummary(
    summary: String,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Overview",
            style = MaterialTheme.typography.titleSmall,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.SemiBold,
        )

        Text(
            text = summary,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurface,
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
            fontWeight = FontWeight.SemiBold,
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
private fun ExperienceWebsiteAction(
    website: String,
    externalUrlLauncher: ExternalUrlLauncher,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.End,
    ) {
        TextButton(
            onClick = {
                externalUrlLauncher.openUrl(website)
            },
        ) {
            Text(
                text = "Visit company →",
                fontWeight = FontWeight.SemiBold,
            )
        }
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
                    width = 220.dp,
                    height = 32.dp,
                )

                SkeletonText(
                    width = 320.dp,
                    height = 18.dp,
                )

                SkeletonText(
                    width = 90.dp,
                    height = 16.dp,
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
            fontWeight = FontWeight.Bold,
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
            Text(
                text = "Retry",
                fontWeight = FontWeight.SemiBold,
            )
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
            fontWeight = FontWeight.Bold,
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

    return "${experience.startDate} — $end"
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