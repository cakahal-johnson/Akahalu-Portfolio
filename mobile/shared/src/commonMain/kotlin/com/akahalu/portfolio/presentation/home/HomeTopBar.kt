package com.akahalu.portfolio.presentation.home

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing

@Composable
fun HomeTopBar(
    isDarkTheme: Boolean,
    onThemeToggle: () -> Unit,
    onHireMe: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Surface(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        color = MaterialTheme.colorScheme.surface,
        tonalElevation = 1.dp,
        shadowElevation = 2.dp,
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(
                    horizontal = AkahaluSpacing.Small,
                    vertical = 6.dp,
                ),
            horizontalArrangement = Arrangement.spacedBy(
                4.dp,
            ),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Akahalu Portfolio",
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurface,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
            )

            IconButton(
                onClick = onThemeToggle,
                modifier = Modifier
                    .size(48.dp)
                    .semantics {
                        contentDescription =
                            if (isDarkTheme) {
                                "Switch to light mode"
                            } else {
                                "Switch to dark mode"
                            }
                    },
            ) {
                ThemeModeIcon(
                    isDarkTheme = isDarkTheme,
                )
            }

            Button(
                onClick = onHireMe,
                modifier = Modifier.size(
                    width = 104.dp,
                    height = 44.dp,
                ),
                shape = RoundedCornerShape(50),
            ) {
                Text(
                    text = "Hire Me",
                    fontWeight = FontWeight.SemiBold,
                )
            }
        }
    }
}

@Composable
private fun ThemeModeIcon(
    isDarkTheme: Boolean,
) {
    val iconColor = MaterialTheme.colorScheme.onSurface
    val surfaceColor = MaterialTheme.colorScheme.surface

    Canvas(
        modifier = Modifier.size(24.dp),
    ) {
        val center = Offset(
            x = size.width / 2f,
            y = size.height / 2f,
        )

        if (isDarkTheme) {
            drawCircle(
                color = iconColor,
                radius = 8.dp.toPx(),
                center = center,
            )

            drawCircle(
                color = surfaceColor,
                radius = 8.dp.toPx(),
                center = Offset(
                    x = center.x + 4.dp.toPx(),
                    y = center.y - 4.dp.toPx(),
                ),
            )
        } else {
            drawCircle(
                color = iconColor,
                radius = 5.dp.toPx(),
                center = center,
            )

            val rayStart = 9.dp.toPx()
            val rayEnd = 11.dp.toPx()

            val angles = listOf(
                0f,
                45f,
                90f,
                135f,
                180f,
                225f,
                270f,
                315f,
            )

            angles.forEach { angle ->
                val radians =
                    angle * kotlin.math.PI / 180.0

                val start = Offset(
                    x = center.x +
                            kotlin.math.cos(radians).toFloat() * rayStart,
                    y = center.y +
                            kotlin.math.sin(radians).toFloat() * rayStart,
                )

                val end = Offset(
                    x = center.x +
                            kotlin.math.cos(radians).toFloat() * rayEnd,
                    y = center.y +
                            kotlin.math.sin(radians).toFloat() * rayEnd,
                )

                drawLine(
                    color = iconColor,
                    start = start,
                    end = end,
                    strokeWidth = 1.8.dp.toPx(),
                    cap = StrokeCap.Round,
                )
            }
        }
    }
}