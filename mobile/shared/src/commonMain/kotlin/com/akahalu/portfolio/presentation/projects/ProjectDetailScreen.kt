package com.akahalu.portfolio.presentation.projects

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.Project

@Composable
fun ProjectDetailScreen(
    project: Project,
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
            text = project.title,
            style = MaterialTheme.typography.headlineMedium,
        )

        Text(
            text = project.shortDescription,
            style = MaterialTheme.typography.bodyLarge,
        )

        project.description?.let { description ->
            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        project.category?.let { category ->
            Text(
                text = "Category: ${category.name}",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.primary,
            )
        }

        if (project.technologies.isNotEmpty()) {
            Text(
                text = "Technologies: ${
                    project.technologies.joinToString(", ") {
                        it.name
                    }
                }",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
    }
}