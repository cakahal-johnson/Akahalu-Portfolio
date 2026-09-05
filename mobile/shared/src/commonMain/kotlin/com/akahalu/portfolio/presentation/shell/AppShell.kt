package com.akahalu.portfolio.presentation.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import com.akahalu.portfolio.core.navigation.AppDestination

data class TopLevelNavigationItem(
    val destination: AppDestination,
    val label: String,
    val icon: String,
)

private val topLevelNavigationItems = listOf(
    TopLevelNavigationItem(
        destination = AppDestination.Home,
        label = "Home",
        icon = "H",
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Projects,
        label = "Projects",
        icon = "P",
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Experience,
        label = "Experience",
        icon = "E",
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Skills,
        label = "Skills",
        icon = "S",
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Contact,
        label = "Contact",
        icon = "C",
    ),
)

@Composable
fun AppNavigationBar(
    currentDestination: AppDestination,
    onDestinationSelected: (AppDestination) -> Unit,
) {
    NavigationBar {
        topLevelNavigationItems.forEach { item ->
            NavigationBarItem(
                selected = currentDestination == item.destination,
                onClick = {
                    onDestinationSelected(item.destination)
                },
                icon = {
                    Text(text = item.icon)
                },
                label = {
                    Text(text = item.label)
                },
            )
        }
    }
}

@Composable
fun PlaceholderScreen(
    title: String,
    subtitle: String,
) {
    Column(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = title,
            style = MaterialTheme.typography.headlineMedium,
        )

        Text(
            text = subtitle,
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}