package com.akahalu.portfolio.presentation.experience

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.EmploymentType
import com.akahalu.portfolio.domain.portfolio.model.Experience
import com.akahalu.portfolio.domain.portfolio.model.ExperienceLocationType

@Composable
fun ExperienceScreen(
    uiState: ExperienceUiState,
    modifier: Modifier = Modifier,
) {
    when (uiState) {
        ExperienceUiState.Loading -> {
            Text(
                text = "Loading experience...",
                modifier = modifier.padding(
                    AkahaluSpacing.Large,
                ),
            )
        }

        is ExperienceUiState.Error -> {
            Text(
                text = uiState.message,
                modifier = modifier.padding(
                    AkahaluSpacing.Large,
                ),
                color = MaterialTheme.colorScheme.error,
            )
        }

        is ExperienceUiState.Success -> {
            if (uiState.experiences.isEmpty()) {
                Text(
                    text = "No experience available.",
                    modifier = modifier.padding(
                        AkahaluSpacing.Large,
                    ),
                )
            } else {
                LazyColumn(
                    modifier = modifier.fillMaxSize(),
                    verticalArrangement =
                        Arrangement.spacedBy(
                            AkahaluSpacing.Medium,
                        ),
                    contentPadding =
                        PaddingValues(
                            AkahaluSpacing.Large,
                        ),
                ) {
                    items(
                        items = uiState.experiences,
                        key = { experience ->
                            experience.id
                        },
                    ) { experience ->
                        ExperienceCard(
                            experience = experience,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ExperienceCard(
    experience: Experience,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.padding(
                AkahaluSpacing.Large,
            ),
            verticalArrangement =
                Arrangement.spacedBy(
                    AkahaluSpacing.Small,
                ),
        ) {
            Text(
                text = experience.jobTitle,
                style = MaterialTheme.typography.titleLarge,
            )

            Text(
                text = experience.companyName,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
            )

            Text(
                text = formatDateRange(experience),
                style = MaterialTheme.typography.bodyMedium,
                color =
                    MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Text(
                text = formatEmploymentType(
                    experience.employmentType,
                ),
                style = MaterialTheme.typography.labelMedium,
            )

            Text(
                text = formatLocation(experience),
                style = MaterialTheme.typography.labelMedium,
                color =
                    MaterialTheme.colorScheme.onSurfaceVariant,
            )

            Text(
                text = experience.summary,
                style = MaterialTheme.typography.bodyMedium,
            )

            if (experience.isCurrent) {
                Text(
                    text = "Current",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }

            if (experience.isFeatured) {
                Text(
                    text = "Featured",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
        }
    }
}

private fun formatDateRange(
    experience: Experience,
): String {
    val end =
        if (experience.isCurrent) {
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
    val type =
        when (experience.locationType) {
            ExperienceLocationType.ONSITE -> "On-site"
            ExperienceLocationType.REMOTE -> "Remote"
            ExperienceLocationType.HYBRID -> "Hybrid"
        }

    return experience.location
        ?.let { "$type | $it" }
        ?: type
}