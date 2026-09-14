package com.akahalu.portfolio.presentation.welcome

import akahaluportfoliomobile.shared.generated.resources.Res
import akahaluportfoliomobile.shared.generated.resources.logo
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBars
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.designsystem.tokens.AkahaluSpacing
import org.jetbrains.compose.resources.painterResource

@Composable
fun WelcomeScreen(
    modifier: Modifier = Modifier,
    onViewProjects: () -> Unit,
    onAbout: () -> Unit,
    onHireMe: () -> Unit,
) {
    val colorScheme = MaterialTheme.colorScheme

    BoxWithConstraints(
        modifier = modifier
            .fillMaxSize()
            .background(
                brush = Brush.verticalGradient(
                    colors = listOf(
                        colorScheme.primaryContainer,
                        colorScheme.background,
                        colorScheme.background,
                    ),
                ),
            )
            .windowInsetsPadding(
                WindowInsets.navigationBars,
            ),
    ) {
        val isLandscape = maxWidth > maxHeight

        val logoSize = if (isLandscape) {
            120.dp
        } else {
            180.dp
        }

        val contentSpacing = if (isLandscape) {
            AkahaluSpacing.Small
        } else {
            AkahaluSpacing.Medium
        }

        val sectionSpacing = if (isLandscape) {
            AkahaluSpacing.Medium
        } else {
            AkahaluSpacing.Large
        }

        WelcomeWaveBackground(
            modifier = Modifier.align(
                Alignment.BottomCenter,
            ),
            compact = isLandscape,
        )

        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(
                    rememberScrollState(),
                )
                .padding(
                    horizontal = if (isLandscape) {
                        AkahaluSpacing.Large
                    } else {
                        AkahaluSpacing.Large
                    },
                    vertical = if (isLandscape) {
                        AkahaluSpacing.Medium
                    } else {
                        AkahaluSpacing.Large
                    },
                ),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Surface(
                shape = RoundedCornerShape(
                    if (isLandscape) {
                        22.dp
                    } else {
                        28.dp
                    },
                ),
                color = colorScheme.surface,
                tonalElevation = 2.dp,
                shadowElevation = 4.dp,
            ) {
                Image(
                    painter = painterResource(
                        Res.drawable.logo,
                    ),
                    contentDescription = "AlphaDev Akahalu logo",
                    modifier = Modifier
                        .size(logoSize)
                        .padding(
                            if (isLandscape) {
                                12.dp
                            } else {
                                16.dp
                            },
                        )
                        .clip(
                            RoundedCornerShape(
                                if (isLandscape) {
                                    16.dp
                                } else {
                                    20.dp
                                },
                            ),
                        ),
                    contentScale = ContentScale.Fit,
                )
            }

            Spacer(
                modifier = Modifier.height(
                    sectionSpacing,
                ),
            )

            Text(
                text = "PORTFOLIO",
                style = MaterialTheme.typography.labelLarge,
                color = colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
                letterSpacing = MaterialTheme.typography.labelLarge.letterSpacing,
            )

            Spacer(
                modifier = Modifier.height(
                    contentSpacing,
                ),
            )

            Text(
                text = "Build. Design. Ship.",
                style = if (isLandscape) {
                    MaterialTheme.typography.headlineMedium
                } else {
                    MaterialTheme.typography.headlineLarge
                },
                color = colorScheme.onBackground,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center,
            )

            Spacer(
                modifier = Modifier.height(
                    contentSpacing,
                ),
            )

            Text(
                text = "A curated selection of projects, ideas, and experiences.",
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(
                        horizontal = AkahaluSpacing.Small,
                    ),
                style = if (isLandscape) {
                    MaterialTheme.typography.bodyMedium
                } else {
                    MaterialTheme.typography.bodyLarge
                },
                color = colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )

            Spacer(
                modifier = Modifier.height(
                    sectionSpacing,
                ),
            )

            Button(
                onClick = onViewProjects,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp)
                    .semantics {
                        contentDescription = "View portfolio projects"
                    },
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = "View Projects",
                    fontWeight = FontWeight.SemiBold,
                )
            }

            Spacer(
                modifier = Modifier.height(
                    contentSpacing,
                ),
            )

            OutlinedButton(
                onClick = onAbout,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp)
                    .semantics {
                        contentDescription = "About Akahalu"
                    },
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = "About Me",
                    fontWeight = FontWeight.SemiBold,
                )
            }

            Spacer(
                modifier = Modifier.height(
                    contentSpacing,
                ),
            )

            OutlinedButton(
                onClick = onHireMe,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp)
                    .semantics {
                        contentDescription = "Hire Akahalu or start a project"
                    },
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = "Hire Me",
                    fontWeight = FontWeight.SemiBold,
                )
            }

            Spacer(
                modifier = Modifier.height(
                    if (isLandscape) {
                        AkahaluSpacing.Medium
                    } else {
                        AkahaluSpacing.Large
                    },
                ),
            )
        }
    }
}

@Composable
private fun WelcomeWaveBackground(
    modifier: Modifier = Modifier,
    compact: Boolean,
) {
    Canvas(
        modifier = modifier
            .fillMaxWidth()
            .height(
                if (compact) {
                    105.dp
                } else {
                    145.dp
                },
            ),
    ) {
        val waveHeight = size.height

        fun createWavePath(
            startY: Float,
            firstControlY: Float,
            secondControlY: Float,
            middleY: Float,
            secondFirstControlY: Float,
            secondSecondControlY: Float,
            endY: Float,
        ): Path {
            return Path().apply {
                moveTo(
                    x = 0f,
                    y = startY,
                )

                cubicTo(
                    x1 = size.width * 0.16f,
                    y1 = firstControlY,
                    x2 = size.width * 0.30f,
                    y2 = secondControlY,
                    x3 = size.width * 0.48f,
                    y3 = middleY,
                )

                cubicTo(
                    x1 = size.width * 0.66f,
                    y1 = secondFirstControlY,
                    x2 = size.width * 0.82f,
                    y2 = secondSecondControlY,
                    x3 = size.width,
                    y3 = endY,
                )

                lineTo(
                    x = size.width,
                    y = waveHeight,
                )

                lineTo(
                    x = 0f,
                    y = waveHeight,
                )

                close()
            }
        }

        val backWave = createWavePath(
            startY = waveHeight * 0.58f,
            firstControlY = waveHeight * 0.42f,
            secondControlY = waveHeight * 0.72f,
            middleY = waveHeight * 0.55f,
            secondFirstControlY = waveHeight * 0.40f,
            secondSecondControlY = waveHeight * 0.68f,
            endY = waveHeight * 0.50f,
        )

        drawPath(
            path = backWave,
            brush = Brush.verticalGradient(
                colors = listOf(
                    Color(0xFFB8D9F0).copy(
                        alpha = 0.18f,
                    ),
                    Color(0xFFB8D9F0).copy(
                        alpha = 0.30f,
                    ),
                ),
            ),
        )

        val middleWave = createWavePath(
            startY = waveHeight * 0.68f,
            firstControlY = waveHeight * 0.50f,
            secondControlY = waveHeight * 0.82f,
            middleY = waveHeight * 0.64f,
            secondFirstControlY = waveHeight * 0.48f,
            secondSecondControlY = waveHeight * 0.78f,
            endY = waveHeight * 0.59f,
        )

        drawPath(
            path = middleWave,
            brush = Brush.verticalGradient(
                colors = listOf(
                    Color(0xFFA9D3ED).copy(
                        alpha = 0.20f,
                    ),
                    Color(0xFFA9D3ED).copy(
                        alpha = 0.34f,
                    ),
                ),
            ),
        )

        val frontWave = createWavePath(
            startY = waveHeight * 0.78f,
            firstControlY = waveHeight * 0.64f,
            secondControlY = waveHeight * 0.90f,
            middleY = waveHeight * 0.74f,
            secondFirstControlY = waveHeight * 0.60f,
            secondSecondControlY = waveHeight * 0.88f,
            endY = waveHeight * 0.70f,
        )

        drawPath(
            path = frontWave,
            brush = Brush.verticalGradient(
                colors = listOf(
                    Color(0xFF8FC8E8).copy(
                        alpha = 0.20f,
                    ),
                    Color(0xFF8FC8E8).copy(
                        alpha = 0.30f,
                    ),
                ),
            ),
        )

        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(
                    Color.White.copy(alpha = 0.12f),
                    Color.Transparent,
                ),
            ),
            radius = size.width * 0.42f,
            center = Offset(
                x = size.width * 0.20f,
                y = waveHeight * 0.82f,
            ),
        )
    }
}