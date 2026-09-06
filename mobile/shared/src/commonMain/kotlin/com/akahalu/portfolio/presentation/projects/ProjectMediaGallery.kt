package com.akahalu.portfolio.presentation.projects

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.SubcomposeAsyncImage
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import com.akahalu.portfolio.domain.portfolio.model.ProjectMedia
import com.akahalu.portfolio.domain.portfolio.model.ProjectMediaType

@Composable
fun ProjectMediaGallery(
    media: List<ProjectMedia>,
    modifier: Modifier = Modifier,
) {
    val orderedMedia = media.sortedWith(
        compareByDescending<ProjectMedia> { it.isPrimary }
            .thenBy { it.sortOrder }
            .thenBy { it.id },
    )

    if (orderedMedia.isEmpty()) {
        return
    }

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Project Media",
            style = MaterialTheme.typography.titleMedium,
        )

        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Medium,
            ),
        ) {
            items(
                items = orderedMedia,
                key = { it.id },
            ) { projectMedia ->
                ProjectMediaItem(
                    media = projectMedia,
                )
            }
        }
    }
}

@Composable
private fun ProjectMediaItem(
    media: ProjectMedia,
    modifier: Modifier = Modifier,
) {
    when (media.mediaType) {
        ProjectMediaType.IMAGE -> {
            ProjectImageMedia(
                media = media,
                modifier = modifier,
            )
        }

        ProjectMediaType.VIDEO,
        ProjectMediaType.DEMO,
        ProjectMediaType.DOCUMENT,
        ProjectMediaType.OTHER,
            -> {
            ProjectNonImageMedia(
                media = media,
                modifier = modifier,
            )
        }
    }
}

@Composable
private fun ProjectImageMedia(
    media: ProjectMedia,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .size(
                width = 280.dp,
                height = 190.dp,
            )
            .clip(
                RoundedCornerShape(
                    16.dp,
                ),
            )
            .background(
                MaterialTheme.colorScheme.surfaceVariant,
            ),
        contentAlignment = Alignment.Center,
    ) {
        SubcomposeAsyncImage(
            model = media.url,
            contentDescription = media.altText
                ?: media.caption
                ?: "Project image",
            modifier = Modifier.fillMaxWidth(),
            contentScale = ContentScale.Crop,
            loading = {
                CircularProgressIndicator(
                    modifier = Modifier.size(
                        28.dp,
                    ),
                )
            },
            error = {
                MediaFallback(
                    media = media,
                )
            },
        )
    }
}

@Composable
private fun ProjectNonImageMedia(
    media: ProjectMedia,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier = modifier
            .size(
                width = 280.dp,
                height = 190.dp,
            )
            .clip(
                RoundedCornerShape(
                    16.dp,
                ),
            )
            .background(
                MaterialTheme.colorScheme.surfaceVariant,
            )
            .padding(
                AkahaluSpacing.Large,
            ),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            Text(
                text = media.mediaType.displayName(),
                style = MaterialTheme.typography.titleMedium,
            )

            media.caption
                ?.takeIf { it.isNotBlank() }
                ?.let { caption ->
                    Text(
                        text = caption,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
        }
    }
}

@Composable
private fun MediaFallback(
    media: ProjectMedia,
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(
                AkahaluSpacing.Medium,
            ),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(
            AkahaluSpacing.Small,
        ),
    ) {
        Text(
            text = "Image unavailable",
            style = MaterialTheme.typography.bodyMedium,
        )

        media.caption
            ?.takeIf { it.isNotBlank() }
            ?.let { caption ->
                Text(
                    text = caption,
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
    }
}

private fun ProjectMediaType.displayName(): String {
    return when (this) {
        ProjectMediaType.IMAGE -> "Image"
        ProjectMediaType.VIDEO -> "Video"
        ProjectMediaType.DOCUMENT -> "Document"
        ProjectMediaType.DEMO -> "Demo"
        ProjectMediaType.OTHER -> "Media"
    }
}