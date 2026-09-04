package com.akahalu.portfolio

import androidx.compose.runtime.Composable
import com.akahalu.portfolio.core.designsystem.theme.AkahaluPortfolioTheme
import com.akahalu.portfolio.presentation.home.HomeScreen

@Composable
fun App() {
    AkahaluPortfolioTheme {
        HomeScreen()
    }
}