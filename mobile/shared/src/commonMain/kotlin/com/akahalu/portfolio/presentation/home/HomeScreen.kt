package com.akahalu.portfolio.presentation.home


import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.ui.layout.ContentScale
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil3.compose.SubcomposeAsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.components.SkeletonBox
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState
import kotlinx.coroutines.delay


@Composable
fun HomeScreen(
    uiState: PortfolioUiState,
    onProjectSelected: (String) -> Unit,
    onViewProjects: () -> Unit,
    onContact: () -> Unit,
    onRetry: () -> Unit,
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    onSkills: () -> Unit,
) {
    when (uiState) {
        PortfolioUiState.Loading -> {
            HomeLoading(
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onHireMe = onContact,
            )
        }

        is PortfolioUiState.Error -> {
            HomeError(
                message = uiState.message,
                onRetry = onRetry,
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onHireMe = onContact,
            )
        }

        is PortfolioUiState.Success -> {
            HomeContent(
                profile = uiState.profile,
                featuredProjects = uiState.featuredProjects,
                onProjectSelected = onProjectSelected,
                onViewProjects = onViewProjects,
                onContact = onContact,
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onSkills = onSkills,
            )
        }
    }
}

@Composable
private fun HomeLoading(
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    onHireMe: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            vertical = AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
    ) {
        item {
            HomeTopBar(
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onHireMe = onHireMe,
                modifier = Modifier.padding(
                    horizontal = AkahaluSpacing.Medium,
                ),
            )
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                HomeHeroSkeleton()
            }
        }

        item {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                SkeletonText(
                    width = 110.dp,
                    height = 14.dp,
                )

                SkeletonText(
                    width = 220.dp,
                    height = 28.dp,
                )

                SkeletonText(
                    width = null,
                    height = 16.dp,
                )
            }
        }

        items(3) {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                SkeletonCard()
            }
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                SkeletonCard()
            }
        }

        item {
            Spacer(
                modifier = Modifier
                    .height(AkahaluSpacing.Huge)
                    .navigationBarsPadding(),
            )
        }
    }
}

@Composable
private fun HomeHeroSkeleton() {
    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {
        SkeletonBox(
            modifier = Modifier
                .widthIn(max = 280.dp)
                .height(34.dp),
            shape = RoundedCornerShape(50),
        )

        SkeletonText(
            width = 260.dp,
            height = 36.dp,
        )

        SkeletonText(
            width = 300.dp,
            height = 36.dp,
        )

        SkeletonText(
            width = null,
            height = 16.dp,
        )

        SkeletonText(
            width = null,
            height = 16.dp,
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            SkeletonBox(
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                shape = RoundedCornerShape(12.dp),
            )

            SkeletonBox(
                modifier = Modifier
                    .weight(1f)
                    .height(48.dp),
                shape = RoundedCornerShape(12.dp),
            )
        }
    }
}

@Composable
private fun HomeError(
    message: String,
    onRetry: () -> Unit,
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    onHireMe: () -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            vertical = AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
    ) {
        item {
            HomeTopBar(
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onHireMe = onHireMe,
                modifier = Modifier.padding(
                    horizontal = AkahaluSpacing.Medium,
                ),
            )
        }

        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = AkahaluSpacing.Medium,
                    ),
                colors = CardDefaults.cardColors(
                    containerColor =
                        MaterialTheme.colorScheme.errorContainer,
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
                        text = "Something went wrong",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color =
                            MaterialTheme.colorScheme.onErrorContainer,
                    )

                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodyMedium,
                        color =
                            MaterialTheme.colorScheme.onErrorContainer,
                    )

                    Button(
                        onClick = onRetry,
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Text(
                            text = "Retry",
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                }
            }
        }

        item {
            Spacer(
                modifier = Modifier
                    .height(AkahaluSpacing.Huge)
                    .navigationBarsPadding(),
            )
        }
    }
}

@Composable
private fun HomeContent(
    profile: Profile,
    featuredProjects: List<Project>,
    onProjectSelected: (String) -> Unit,
    onViewProjects: () -> Unit,
    onContact: () -> Unit,
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    onSkills: () -> Unit,
) {
    var contentVisible by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(Unit) {
        delay(80)
        contentVisible = true
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            vertical = AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
    ) {
        item {
            HomeTopBar(
                isDarkTheme = isDarkTheme,
                onThemeToggle = onThemeToggle,
                onHireMe = onContact,
                modifier = Modifier.padding(
                    horizontal = AkahaluSpacing.Medium,
                ),
            )
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                AnimatedVisibility(
                    visible = contentVisible,
                    enter = fadeIn(
                        animationSpec = tween(
                            durationMillis = 500,
                            easing = FastOutSlowInEasing,
                        ),
                    ) + slideInVertically(
                        animationSpec = tween(
                            durationMillis = 500,
                            easing = FastOutSlowInEasing,
                        ),
                        initialOffsetY = { it / 4 },
                    ),
                ) {
                    HeroSection(
                        profile = profile,
                        onViewProjects = onViewProjects,
                        onContact = onContact,
                        onSkills = onSkills,
                    )
                }
            }
        }

        if (featuredProjects.isNotEmpty()) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = AkahaluSpacing.Medium),
                ) {
                    SectionHeader(
                        eyebrow = "Selected work",
                        title = "Featured projects",
                        description = "A selection of projects and technical work.",
                    )
                }
            }

            items(
                items = featuredProjects.take(4),
                key = { project -> project.id },
            ) { project ->
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = AkahaluSpacing.Medium),
                ) {
                    AnimatedProjectCard(
                        project = project,
                        onClick = {
                            onProjectSelected(project.slug)
                        },
                    )
                }
            }
        } else {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = AkahaluSpacing.Medium),
                ) {
                    EmptyProjectsCard()
                }
            }
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                AboutPreview(
                    profile = profile,
                )
            }
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                AvailabilitySummary(
                    profile = profile,
                )
            }
        }

        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = AkahaluSpacing.Medium),
            ) {
                HomeFooter(
                    profile = profile,
                )
            }
        }

        item {
            Spacer(
                modifier = Modifier
                    .height(AkahaluSpacing.Huge)
                    .navigationBarsPadding(),
            )
        }
    }
}

@Composable
private fun HeroSection(
    profile: Profile,
    onViewProjects: () -> Unit,
    onContact: () -> Unit,
    onSkills: () -> Unit,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                horizontal = AkahaluSpacing.Medium,
                vertical = AkahaluSpacing.Small,
            ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Medium,
        ),
    ) {

        AvailabilityBadge(
            status = profile.availabilityStatus,
        )

        Text(
            text = profile.professionalTitle,
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        Text(
            text = profile.headline,
            style = MaterialTheme.typography.headlineLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onBackground,
        )

        profile.shortBio
            .takeIf { it.isNotBlank() }
            ?.let { bio ->
                Text(
                    text = bio,
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            Button(
                onClick = onViewProjects,
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = "View Projects",
                    fontWeight = FontWeight.SemiBold,
                )
            }

            OutlinedButton(
                onClick = onContact,
                modifier = Modifier
                    .weight(1f)
                    .height(52.dp),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = "Contact Me",
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }

        if (profile.yearsOfExperience > 0) {
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(14.dp),
                color = MaterialTheme.colorScheme.secondaryContainer,
            ) {
                Text(
                    text = "${profile.yearsOfExperience}+ years of professional experience",
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(
                            horizontal = AkahaluSpacing.Medium,
                            vertical = AkahaluSpacing.Small,
                        ),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSecondaryContainer,
                    fontWeight = FontWeight.Medium,
                )
            }
        }

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Surface(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(35),
            color = MaterialTheme.colorScheme.primaryContainer,
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        start = AkahaluSpacing.Medium,
                        end = AkahaluSpacing.Small,
                        top = 6.dp,
                        bottom = 6.dp,
                    ),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Full-Stack • FastAPI • Next.js • TypeScript • Kotlin",
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    fontWeight = FontWeight.SemiBold,
                    maxLines = 2,
                )

                TextButton(
                    onClick = onSkills,
                ) {
                    Text(
                        text = "More →",
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold,
                    )
                }
            }
        }
    }
}

@Composable
private fun ProfileImage(
    imageUrl: String?,
    displayName: String,
) {
    Box(
        modifier = Modifier
            .size(112.dp)
            .clip(CircleShape)
            .background(
                MaterialTheme.colorScheme.primaryContainer,
            ),
        contentAlignment = Alignment.Center,
    ) {
        if (imageUrl.isNullOrBlank()) {
            ProfileInitials(
                displayName = displayName,
            )
        } else {
            SubcomposeAsyncImage(
                model = imageUrl,
                contentDescription = "$displayName profile photo",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
                loading = {
                    SkeletonBox(
                        modifier = Modifier.fillMaxSize(),
                        shape = CircleShape,
                    )
                },
                error = {
                    ProfileInitials(
                        displayName = displayName,
                    )
                },
            )
        }
    }
}

@Composable
private fun ProfileInitials(
    displayName: String,
) {
    Text(
        text = displayName
            .trim()
            .split(Regex("\\s+"))
            .filter { it.isNotBlank() }
            .take(2)
            .mapNotNull { it.firstOrNull() }
            .joinToString("")
            .ifBlank { "AV" },
        style = MaterialTheme.typography.headlineMedium,
        fontWeight = FontWeight.Bold,
        color = MaterialTheme.colorScheme.onPrimaryContainer,
    )
}

@Composable
private fun AvailabilityBadge(
    status: ProfileAvailabilityStatus,
) {
    val label = when (status) {
        ProfileAvailabilityStatus.AVAILABLE ->
            "Available"

        ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES ->
            "Open to opportunities"

        ProfileAvailabilityStatus.LIMITED_AVAILABILITY ->
            "Limited availability"

        ProfileAvailabilityStatus.UNAVAILABLE ->
            "Currently unavailable"
    }

    Surface(
        shape = RoundedCornerShape(50),
        color = when (status) {
            ProfileAvailabilityStatus.AVAILABLE,
            ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES ->
                MaterialTheme.colorScheme.primaryContainer

            ProfileAvailabilityStatus.LIMITED_AVAILABILITY ->
                MaterialTheme.colorScheme.secondaryContainer

            ProfileAvailabilityStatus.UNAVAILABLE ->
                MaterialTheme.colorScheme.surfaceVariant
        },
    ) {
        Row(
            modifier = Modifier.padding(
                horizontal = AkahaluSpacing.Medium,
                vertical = AkahaluSpacing.Small,
            ),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Box(
                modifier = Modifier
                    .size(8.dp)
                    .clip(CircleShape)
                    .background(
                        when (status) {
                            ProfileAvailabilityStatus.AVAILABLE,
                            ProfileAvailabilityStatus.OPEN_TO_OPPORTUNITIES ->
                                MaterialTheme.colorScheme.primary

                            ProfileAvailabilityStatus.LIMITED_AVAILABILITY ->
                                MaterialTheme.colorScheme.secondary

                            ProfileAvailabilityStatus.UNAVAILABLE ->
                                MaterialTheme.colorScheme.onSurfaceVariant
                        },
                    ),
            )

            Text(
                text = label,
                style = MaterialTheme.typography.labelLarge,
                fontWeight = FontWeight.Medium,
            )
        }
    }
}

@Composable
private fun SectionHeader(
    eyebrow: String,
    title: String,
    description: String,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.ExtraSmall,
        ),
    ) {
        Text(
            text = eyebrow.uppercase(),
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.primary,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = title,
            style = MaterialTheme.typography.headlineSmall,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = description,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
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
        delay(100)
        visible = true
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn(
            animationSpec = tween(450),
        ) + slideInVertically(
            animationSpec = tween(450),
            initialOffsetY = { it / 5 },
        ),
    ) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(onClick = onClick),
            shape = RoundedCornerShape(22.dp),
        ) {
            Column {
                if (!project.thumbnailUrl.isNullOrBlank()) {
                    SubcomposeAsyncImage(
                        model = project.thumbnailUrl,
                        contentDescription = "${project.title} project preview",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(190.dp),
                        contentScale = ContentScale.Crop,
                        loading = {
                            SkeletonBox(
                                modifier = Modifier.fillMaxSize(),
                                shape = RoundedCornerShape(22.dp),
                            )
                        },
                        error = {
                            ProjectThumbnailFallback(
                                title = project.title,
                            )
                        },
                    )
                } else {
                    ProjectThumbnailFallback(
                        title = project.title,
                    )
                }

                Column(
                    modifier = Modifier.padding(
                        AkahaluSpacing.Medium,
                    ),
                    verticalArrangement = Arrangement.spacedBy(
                        AkahaluSpacing.Small,
                    ),
                ) {
                    project.category?.name
                        ?.takeIf { it.isNotBlank() }
                        ?.let { category ->
                            Text(
                                text = category.uppercase(),
                                style = MaterialTheme.typography.labelMedium,
                                color = MaterialTheme.colorScheme.primary,
                                fontWeight = FontWeight.Bold,
                            )
                        }

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
                                        )
                                    }
                                }
                        }
                    }

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
private fun ProjectThumbnailFallback(
    title: String,
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
}

@Composable
private fun EmptyProjectsCard() {
    Card(
        modifier = Modifier.fillMaxWidth(),
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
                text = "Featured work is coming soon.",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )

            Text(
                text = "Projects will appear here once they are published.",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
    }
}

@Composable
private fun AboutPreview(
    profile: Profile,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
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
                text = "About me",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = profile.shortBio,
                style = MaterialTheme.typography.bodyLarge,
            )

            if (profile.location != null || profile.country != null) {
                Text(
                    text = listOfNotNull(
                        profile.location,
                        profile.country,
                    ).joinToString(", "),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun AvailabilitySummary(
    profile: Profile,
) {
    profile.availabilityMessage
        ?.takeIf { it.isNotBlank() }
        ?.let { message ->
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
                        text = "Let's work together",
                        style = MaterialTheme.typography.titleLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                    )

                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onPrimaryContainer,
                    )
                }
            }
        }
}

@Composable
private fun HomeFooter(
    profile: Profile,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                vertical = AkahaluSpacing.Medium,
            ),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = profile.displayName,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.SemiBold,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.ExtraSmall,
            ),
        )

        Text(
            text = profile.professionalTitle,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        profile.primaryEmail
            .takeIf { it.isNotBlank() }
            ?.let { email ->
                TextButton(
                    onClick = {
                        // Platform URL/email launching will be
                        // handled in a dedicated platform integration milestone.
                    },
                ) {
                    Text(email)
                }
            }

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Text(
            text = "© ${profile.displayName}",
            style = MaterialTheme.typography.labelMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
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