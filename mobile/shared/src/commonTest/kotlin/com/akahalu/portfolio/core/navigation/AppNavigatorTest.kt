package com.akahalu.portfolio.core.navigation

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class AppNavigatorTest {

    @Test
    fun initialDestination_isHome() {
        val navigator = AppNavigator()

        assertEquals(
            AppDestination.Home,
            navigator.currentDestination.value,
        )
        assertFalse(navigator.canGoBack())
    }

    @Test
    fun navigateToTopLevel_changesDestinationAndClearsBackStack() {
        val navigator = AppNavigator()

        navigator.navigateToTopLevel(
            AppDestination.Projects,
        )

        assertEquals(
            AppDestination.Projects,
            navigator.currentDestination.value,
        )
        assertFalse(navigator.canGoBack())
    }

    @Test
    fun navigateToProjectDetail_pushesCurrentDestination() {
        val navigator = AppNavigator()

        navigator.navigateToTopLevel(
            AppDestination.Projects,
        )

        navigator.navigateToProjectDetail(
            "akahalu-portfolio",
        )

        assertEquals(
            AppDestination.ProjectDetail(
                slug = "akahalu-portfolio",
            ),
            navigator.currentDestination.value,
        )
        assertTrue(navigator.canGoBack())
    }

    @Test
    fun goBack_returnsToPreviousDestination() {
        val navigator = AppNavigator()

        navigator.navigateToTopLevel(
            AppDestination.Projects,
        )

        navigator.navigateToProjectDetail(
            "akahalu-portfolio",
        )

        val didGoBack = navigator.goBack()

        assertTrue(didGoBack)
        assertEquals(
            AppDestination.Projects,
            navigator.currentDestination.value,
        )
        assertFalse(navigator.canGoBack())
    }

    @Test
    fun goBack_returnsFalse_whenThereIsNoBackStack() {
        val navigator = AppNavigator()

        assertFalse(navigator.goBack())

        assertEquals(
            AppDestination.Home,
            navigator.currentDestination.value,
        )
    }

    @Test
    fun navigatingBetweenTopLevelDestinations_clearsPreviousDetailHistory() {
        val navigator = AppNavigator()

        navigator.navigateToProjectDetail(
            "first-project",
        )

        navigator.navigateToTopLevel(
            AppDestination.Contact,
        )

        assertEquals(
            AppDestination.Contact,
            navigator.currentDestination.value,
        )
        assertFalse(navigator.canGoBack())
    }

    @Test
    fun navigateToProjectDetail_rejectsBlankSlug() {
        val navigator = AppNavigator()

        assertTrue(
            runCatching {
                navigator.navigateToProjectDetail("   ")
            }.isFailure,
        )
    }
}