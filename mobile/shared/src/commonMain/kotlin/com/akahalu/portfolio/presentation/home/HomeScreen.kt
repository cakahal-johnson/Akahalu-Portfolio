package com.akahalu.portfolio.presentation.home

import akahaluportfoliomobile.shared.generated.resources.Res
import akahaluportfoliomobile.shared.generated.resources.logo
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
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
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Profile
import com.akahalu.portfolio.domain.portfolio.model.ProfileAvailabilityStatus
import com.akahalu.portfolio.domain.portfolio.model.Project
import com.akahalu.portfolio.presentation.components.SkeletonBox
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import com.akahalu.portfolio.presentation.portfolio.PortfolioUiState
import kotlinx.coroutines.delay
import org.jetbrains.compose.resources.painterResource

@Composable
fun HomeScreen(
    uiState: PortfolioUiState,
    onProjectSelected: (String) -> Unit,
    onViewProjects: () -> Unit,
    onContact: () -> Unit,
) {
    when (uiState) {
        PortfolioUiState.Loading -> {
            HomeLoading()
        }

        is PortfolioUiState.Error -> {
            HomeError(
                message = uiState.message,
            )
        }

        is PortfolioUiState.Success -> {
            HomeContent(
                profile = uiState.profile,
                featuredProjects = uiState.featuredProjects,
                onProjectSelected = onProjectSelected,
                onViewProjects = onViewProjects,
                onContact = onContact,
            )
        }
    }
}

@Composable
private fun HomeLoading() {
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
            AlphaDevBanner()
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
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(28.dp),
    ) {
        Column(
            modifier = Modifier.padding(
                AkahaluSpacing.Large,
            ),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            SkeletonBox(
                modifier = Modifier.size(112.dp),
                shape = CircleShape,
            )

            SkeletonText(
                width = 150.dp,
                height = 28.dp,
            )

            SkeletonText(
                width = 210.dp,
                height = 22.dp,
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

            SkeletonText(
                width = 210.dp,
                height = 18.dp,
            )
        }
    }
}

@Composable
private fun HomeError(
    message: String,
) {
    Box(
        modifier = Modifier
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
                verticalArrangement = Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
            ) {
                Text(
                    text = "Something went wrong",
                    style = MaterialTheme.typography.headlineSmall,
                )

                Text(
                    text = message,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
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
            AlphaDevBanner()
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
private fun AlphaDevBanner() {
    Surface(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp),
        color = MaterialTheme.colorScheme.surface,
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center,
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp),
                horizontalArrangement = Arrangement.Center,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Image(
                    painter = painterResource(Res.drawable.logo),
                    contentDescription = "AlphaDev Technologies",
                    modifier = Modifier
                        .height(80.dp)
                        .weight(1f)
                        .clip(RoundedCornerShape(25.dp)),
                    contentScale = ContentScale.Fit,
                )

                Box(
                    modifier = Modifier
                        .height(80.dp)
                        .padding(horizontal = 4.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Box(
                        modifier = Modifier
                            .size(6.dp)
                            .clip(CircleShape)
                            .background(
                                MaterialTheme.colorScheme.primary,
                            ),
                    )
                }

                Text(
                    text = "Building Digital Solutions for a Better Tomorrow",
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
    }
}

@Composable
private fun HeroSection(
    profile: Profile,
    onViewProjects: () -> Unit,
    onContact: () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(28.dp),
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
//            ProfileImage(
//                imageUrl = profile.profileImageUrl,
//                displayName = profile.displayName,
//            )

            AvailabilityBadge(
                status = profile.availabilityStatus,
            )

            Text(
                text = "Hello, I'm",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
            )

            Text(
                text = profile.displayName,
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = profile.professionalTitle,
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Text(
                text = profile.headline,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )

            profile.shortBio
                .takeIf { it.isNotBlank() }
                ?.let { bio ->
                    Text(
                        text = bio,
                        style = MaterialTheme.typography.bodyMedium,
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
                    modifier = Modifier.weight(1f),
                ) {
                    Text("View projects")
                }

                OutlinedButton(
                    onClick = onContact,
                    modifier = Modifier.weight(1f),
                ) {
                    Text("Contact me")
                }
            }

            if (profile.yearsOfExperience > 0) {
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.secondaryContainer,
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(
                                horizontal = AkahaluSpacing.Medium,
                                vertical = AkahaluSpacing.Small,
                            ),
                        horizontalArrangement = Arrangement.spacedBy(
                            AkahaluSpacing.Small,
                        ),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Text(
                            text = "${profile.yearsOfExperience}+",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                        )

                        Text(
                            text = "years of professional experience",
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSecondaryContainer,
                        )
                    }
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
            .background(MaterialTheme.colorScheme.primaryContainer),
        contentAlignment = Alignment.Center,
    ) {
        if (!imageUrl.isNullOrBlank()) {
            AsyncImage(
                model = imageUrl,
                contentDescription = "$displayName profile photo",
                modifier = Modifier.fillMaxSize(),
                contentScale = ContentScale.Crop,
            )
        } else {
            Text(
                text = displayName
                    .split(" ")
                    .filter { it.isNotBlank() }
                    .take(2)
                    .mapNotNull { it.firstOrNull() }
                    .joinToString(""),
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
        }
    }
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
                    AsyncImage(
                        model = project.thumbnailUrl,
                        contentDescription = "${project.title} project preview",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(190.dp),
                        contentScale = ContentScale.Crop,
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