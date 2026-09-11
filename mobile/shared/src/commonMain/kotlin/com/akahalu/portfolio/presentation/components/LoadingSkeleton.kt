package com.akahalu.portfolio.presentation.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing

@Composable
fun SkeletonBox(
    modifier: Modifier = Modifier,
    shape: Shape = MaterialTheme.shapes.medium,
) {
    val transition = rememberInfiniteTransition(
        label = "skeleton-pulse",
    )

    val alpha by transition.animateFloat(
        initialValue = 0.45f,
        targetValue = 0.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = 900,
            ),
            repeatMode = RepeatMode.Reverse,
        ),
        label = "skeleton-alpha",
    )

    androidx.compose.foundation.layout.Box(
        modifier = modifier
            .alpha(alpha)
            .background(
                color = MaterialTheme.colorScheme.surfaceVariant,
                shape = shape,
            ),
    )
}

@Composable
fun SkeletonText(
    modifier: Modifier = Modifier,
    width: Dp? = 180.dp,
    height: Dp = 16.dp,
) {
    val skeletonModifier = modifier.height(height)

    SkeletonBox(
        modifier = if (width != null) {
            skeletonModifier.width(width)
        } else {
            skeletonModifier.fillMaxWidth()
        },
        shape = RoundedCornerShape(6.dp),
    )
}

@Composable
fun SkeletonCard(
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = MaterialTheme.shapes.medium,
    ) {
        Column(
            modifier = Modifier.padding(AkahaluSpacing.Large),
            verticalArrangement = Arrangement.spacedBy(
                AkahaluSpacing.Small,
            ),
        ) {
            SkeletonText(
                width = 190.dp,
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

            SkeletonText(
                width = 90.dp,
                height = 14.dp,
            )
        }
    }
}