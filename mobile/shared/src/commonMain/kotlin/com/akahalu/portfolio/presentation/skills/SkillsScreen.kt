package com.akahalu.portfolio.presentation.skills

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
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
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory
import com.akahalu.portfolio.presentation.components.SkeletonCard
import com.akahalu.portfolio.presentation.components.SkeletonText
import kotlinx.coroutines.delay

@Composable
fun SkillsScreen(
    uiState: SkillsUiState,
    modifier: Modifier = Modifier,
) {
    when (uiState) {
        SkillsUiState.Loading -> {
            SkillsLoadingScreen(
                modifier = modifier,
            )
        }

        is SkillsUiState.Success -> {
            SkillsSuccessScreen(
                technologies = uiState.technologies,
                modifier = modifier,
            )
        }

        is SkillsUiState.Error -> {
            SkillsErrorScreen(
                message = uiState.message,
                modifier = modifier,
            )
        }
    }
}

@Composable
private fun SkillsLoadingScreen(
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
                    width = 240.dp,
                    height = 32.dp,
                )

                SkeletonText(
                    width = 320.dp,
                    height = 18.dp,
                )

                SkeletonText(
                    width = 110.dp,
                    height = 16.dp,
                )
            }
        }

        item {
            SkeletonCard()
        }

        item {
            SkeletonCard()
        }

        item {
            SkeletonCard()
        }
    }
}

@Composable
private fun SkillsErrorScreen(
    message: String,
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
            text = "Unable to load skills",
            style = MaterialTheme.typography.titleLarge,
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
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun SkillsSuccessScreen(
    technologies: List<ProjectTechnology>,
    modifier: Modifier = Modifier,
) {
    if (technologies.isEmpty()) {
        SkillsEmptyState(
            modifier = modifier,
        )

        return
    }

    val groupedTechnologies = technologies
        .groupBy(ProjectTechnology::category)
        .mapValues { (_, items) ->
            items.sortedWith(
                compareBy<ProjectTechnology> {
                    it.sortOrder
                }.thenBy {
                    it.name.lowercase()
                },
            )
        }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
        contentPadding = PaddingValues(
            horizontal = AkahaluSpacing.Medium,
            vertical = AkahaluSpacing.Large,
        ),
    ) {
        item {
            SkillsHeader(
                technologyCount = technologies.size,
                categoryCount = groupedTechnologies.size,
            )
        }

        ProjectTechnologyCategory.entries.forEach { category ->
            val categoryTechnologies = groupedTechnologies[category]
                ?: return@forEach

            item(
                key = "category-${category.name}",
            ) {
                SkillsCategoryHeader(
                    category = category,
                    count = categoryTechnologies.size,
                )
            }

            items(
                items = categoryTechnologies,
                key = { technology ->
                    technology.id
                },
            ) { technology ->
                TechnologyCard(
                    technology = technology,
                )
            }
        }
    }
}

@Composable
private fun SkillsHeader(
    technologyCount: Int,
    categoryCount: Int,
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Skills & Technologies",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        Text(
            text = "Technologies and tools I use to build modern digital products.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            SkillsStatCard(
                value = technologyCount.toString(),
                label = "Technologies",
                modifier = Modifier.weight(1f),
            )

            SkillsStatCard(
                value = categoryCount.toString(),
                label = "Categories",
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun SkillsStatCard(
    value: String,
    label: String,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(16.dp),
        color = MaterialTheme.colorScheme.primaryContainer,
    ) {
        Column(
            modifier = Modifier.padding(
                horizontal = AkahaluSpacing.Medium,
                vertical = AkahaluSpacing.Small,
            ),
        ) {
            Text(
                text = value,
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = label,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onPrimaryContainer,
            )
        }
    }
}

@Composable
private fun SkillsCategoryHeader(
    category: ProjectTechnologyCategory,
    count: Int,
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.ExtraSmall,
            ),
        ) {
            Text(
                text = category.displayName(),
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )

            Text(
                text = categoryDescription(category),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        Surface(
            shape = RoundedCornerShape(50),
            color = MaterialTheme.colorScheme.surfaceVariant,
        ) {
            Text(
                text = count.toString(),
                modifier = Modifier.padding(
                    horizontal = 10.dp,
                    vertical = 5.dp,
                ),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                fontWeight = FontWeight.SemiBold,
            )
        }
    }
}

@Composable
private fun TechnologyCard(
    technology: ProjectTechnology,
) {
    var visible by remember {
        mutableStateOf(false)
    }

    LaunchedEffect(technology.id) {
        delay(50)
        visible = true
    }

    AnimatedVisibility(
        visible = visible,
        enter = fadeIn() + slideInVertically(
            initialOffsetY = { 16 },
        ),
    ) {
        Card(
            modifier = Modifier.fillMaxWidth(),
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
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(
                        AkahaluSpacing.Medium,
                    ),
                    verticalAlignment = Alignment.Top,
                ) {
                    TechnologyIcon(
                        technology = technology,
                    )

                    Column(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(
                            AkahaluSpacing.ExtraSmall,
                        ),
                    ) {
                        Text(
                            text = technology.name,
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold,
                        )

                        Text(
                            text = technology.category.displayName(),
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.SemiBold,
                        )
                    }
                }

                technology.description
                    ?.takeIf { it.isNotBlank() }
                    ?.let { description ->
                        Text(
                            text = description,
                            style = MaterialTheme.typography.bodyMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                        )
                    }

                technology.officialUrl
                    ?.takeIf { it.isNotBlank() }
                    ?.let {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.End,
                        ) {
                            TextButton(
                                onClick = {
                                    // URL action remains intentionally
                                    // presentation-safe for now.
                                },
                            ) {
                                Text(
                                    text = "Official website →",
                                    fontWeight = FontWeight.SemiBold,
                                )
                            }
                        }
                    }
            }
        }
    }
}

@Composable
private fun TechnologyIcon(
    technology: ProjectTechnology,
) {
    val iconText = technology.icon
        ?.takeIf { it.isNotBlank() }
        ?.take(2)
        ?.uppercase()
        ?: technologyInitials(technology.name)

    Box(
        modifier = Modifier
            .size(52.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(
                technologyColor(
                    technology.color,
                ),
            ),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = iconText,
            style = MaterialTheme.typography.labelLarge,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onPrimary,
        )
    }
}

@Composable
private fun SkillsEmptyState(
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
            text = "Skills & Technologies",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
        )

        Spacer(
            modifier = Modifier.height(
                AkahaluSpacing.Small,
            ),
        )

        Text(
            text = "No skills and technologies are available yet.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

private fun ProjectTechnologyCategory.displayName(): String {
    return when (this) {
        ProjectTechnologyCategory.LANGUAGE -> "Languages"
        ProjectTechnologyCategory.FRAMEWORK -> "Frameworks"
        ProjectTechnologyCategory.LIBRARY -> "Libraries"
        ProjectTechnologyCategory.DATABASE -> "Databases"
        ProjectTechnologyCategory.PLATFORM -> "Platforms"
        ProjectTechnologyCategory.CLOUD -> "Cloud"
        ProjectTechnologyCategory.DEVOPS -> "DevOps"
        ProjectTechnologyCategory.TESTING -> "Testing"
        ProjectTechnologyCategory.TOOL -> "Tools"
        ProjectTechnologyCategory.SERVICE -> "Services"
        ProjectTechnologyCategory.OTHER -> "Other"
    }
}

private fun categoryDescription(
    category: ProjectTechnologyCategory,
): String {
    return when (category) {
        ProjectTechnologyCategory.LANGUAGE ->
            "Programming languages"

        ProjectTechnologyCategory.FRAMEWORK ->
            "Application frameworks"

        ProjectTechnologyCategory.LIBRARY ->
            "Reusable development libraries"

        ProjectTechnologyCategory.DATABASE ->
            "Data storage and database systems"

        ProjectTechnologyCategory.PLATFORM ->
            "Platforms and application environments"

        ProjectTechnologyCategory.CLOUD ->
            "Cloud infrastructure and services"

        ProjectTechnologyCategory.DEVOPS ->
            "Deployment and engineering operations"

        ProjectTechnologyCategory.TESTING ->
            "Testing and quality tools"

        ProjectTechnologyCategory.TOOL ->
            "Development and productivity tools"

        ProjectTechnologyCategory.SERVICE ->
            "External services and integrations"

        ProjectTechnologyCategory.OTHER ->
            "Other technologies"
    }
}

private fun technologyInitials(
    name: String,
): String {
    val words = name
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

        else -> "T"
    }
}

private fun technologyColor(
    value: String?,
): Color {
    val hex = value
        ?.removePrefix("#")
        ?.takeIf { it.length == 6 }

    if (hex == null) {
        return Color(0xFF2563EB)
    }

    return runCatching {
        val red = hex.substring(0, 2).toInt(16)
        val green = hex.substring(2, 4).toInt(16)
        val blue = hex.substring(4, 6).toInt(16)

        Color(
            red = red,
            green = green,
            blue = blue,
        )
    }.getOrElse {
        Color(0xFF2563EB)
    }
}