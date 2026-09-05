package com.akahalu.portfolio.presentation.skills

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnology
import com.akahalu.portfolio.domain.portfolio.model.ProjectTechnologyCategory

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
    Column(
        modifier = modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
    ) {
        CircularProgressIndicator(
            modifier = Modifier.padding(
                horizontal = AkahaluSpacing.Large,
            ),
        )
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
    ) {
        Text(
            text = "Unable to load skills",
            style = MaterialTheme.typography.headlineSmall,
        )

        Text(
            text = message,
            modifier = Modifier.padding(
                top = AkahaluSpacing.Small,
            ),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
private fun SkillsSuccessScreen(
    technologies: List<ProjectTechnology>,
    modifier: Modifier = Modifier,
) {
    if (technologies.isEmpty()) {
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.Center,
        ) {
            Text(
                text = "Skills & Technologies",
                style = MaterialTheme.typography.headlineMedium,
            )

            Text(
                text = "No skills and technologies are available yet.",
                modifier = Modifier.padding(
                    top = AkahaluSpacing.Small,
                ),
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        return
    }

    val groupedTechnologies = technologies.groupBy(
        keySelector = ProjectTechnology::category,
    )

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(
            horizontal = AkahaluSpacing.Large,
            vertical = AkahaluSpacing.Large,
        ),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Large,
        ),
    ) {
        item {
            Column {
                Text(
                    text = "Skills & Technologies",
                    style = MaterialTheme.typography.headlineMedium,
                )

                Text(
                    text = "Technologies and tools used across my professional projects.",
                    modifier = Modifier.padding(
                        top = AkahaluSpacing.Small,
                    ),
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }

        ProjectTechnologyCategory.entries.forEach { category ->
            val categoryTechnologies = groupedTechnologies[category]
                ?: return@forEach

            item(key = "category-${category.name}") {
                Text(
                    text = category.displayName(),
                    style = MaterialTheme.typography.titleLarge,
                    modifier = Modifier.padding(
                        top = AkahaluSpacing.Small,
                    ),
                )
            }

            items(
                items = categoryTechnologies,
                key = { technology -> technology.id },
            ) { technology ->
                TechnologyCard(
                    technology = technology,
                )
            }
        }
    }
}

@Composable
private fun TechnologyCard(
    technology: ProjectTechnology,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(),
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Medium),
        ) {
            Text(
                text = technology.name,
                style = MaterialTheme.typography.titleMedium,
            )

            Text(
                text = technology.category.displayName(),
                modifier = Modifier.padding(
                    top = AkahaluSpacing.ExtraSmall,
                ),
                style = MaterialTheme.typography.labelMedium,
            )

            technology.description
                ?.takeIf { it.isNotBlank() }
                ?.let { description ->
                    Text(
                        text = description,
                        modifier = Modifier.padding(
                            top = AkahaluSpacing.Small,
                        ),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

            technology.officialUrl
                ?.takeIf { it.isNotBlank() }
                ?.let { officialUrl ->
                    Text(
                        text = officialUrl,
                        modifier = Modifier.padding(
                            top = AkahaluSpacing.Small,
                        ),
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
        }
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