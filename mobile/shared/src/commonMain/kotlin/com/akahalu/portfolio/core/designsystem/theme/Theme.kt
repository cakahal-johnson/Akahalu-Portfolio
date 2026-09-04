package com.akahalu.portfolio.core.designsystem.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColorScheme = lightColorScheme(
    primary = AkahaluBlue,
    onPrimary = AkahaluLightSurface,
    background = AkahaluLightBackground,
    onBackground = AkahaluLightOnBackground,
    surface = AkahaluLightSurface,
    onSurface = AkahaluLightOnSurface,
)

private val DarkColorScheme = darkColorScheme(
    primary = AkahaluBlueDark,
    onPrimary = AkahaluDarkOnSurface,
    background = AkahaluDarkBackground,
    onBackground = AkahaluDarkOnBackground,
    surface = AkahaluDarkSurface,
    onSurface = AkahaluDarkOnSurface,
)

@Composable
fun AkahaluPortfolioTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme =
        if (darkTheme) {
            DarkColorScheme
        } else {
            LightColorScheme
        }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AkahaluTypography,
        shapes = AkahaluShapes,
        content = content,
    )
}