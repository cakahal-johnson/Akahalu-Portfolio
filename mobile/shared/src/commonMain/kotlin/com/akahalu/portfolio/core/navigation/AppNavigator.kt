package com.akahalu.portfolio.core.navigation

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class AppNavigator(
    initialDestination: AppDestination = AppDestination.Home,
) {

    private val backStack = ArrayDeque<AppDestination>()

    private val _currentDestination =
        MutableStateFlow<AppDestination>(initialDestination)

    val currentDestination: StateFlow<AppDestination> =
        _currentDestination.asStateFlow()

    fun navigateToTopLevel(destination: AppDestination) {
        require(destination !is AppDestination.ProjectDetail) {
            "Project detail is not a top-level destination."
        }

        backStack.clear()
        _currentDestination.value = destination
    }

    fun navigateToProjectDetail(slug: String) {
        require(slug.isNotBlank()) {
            "Project slug must not be blank."
        }

        backStack.addLast(_currentDestination.value)
        _currentDestination.value = AppDestination.ProjectDetail(
            slug = slug,
        )
    }

    fun goBack(): Boolean {
        if (backStack.isEmpty()) {
            return false
        }

        _currentDestination.value = backStack.removeLast()
        return true
    }

    fun canGoBack(): Boolean = backStack.isNotEmpty()
}