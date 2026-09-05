package com.akahalu.portfolio.core.navigation

sealed interface AppDestination {
    data object Home : AppDestination

    data object Projects : AppDestination

    data class ProjectDetail(
        val slug: String,
    ) : AppDestination

    data object Experience : AppDestination

    data object Skills : AppDestination

    data object Contact : AppDestination
}