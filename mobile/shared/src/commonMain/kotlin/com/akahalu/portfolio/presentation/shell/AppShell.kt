package com.akahalu.portfolio.presentation.shell

import akahaluportfoliomobile.shared.generated.resources.Res
import akahaluportfoliomobile.shared.generated.resources.ic_contact
import akahaluportfoliomobile.shared.generated.resources.ic_experience
import akahaluportfoliomobile.shared.generated.resources.ic_home
import akahaluportfoliomobile.shared.generated.resources.ic_projects
import akahaluportfoliomobile.shared.generated.resources.ic_skills
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.unit.dp
import com.akahalu.portfolio.core.navigation.AppDestination
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource

data class TopLevelNavigationItem(
    val destination: AppDestination,
    val label: String,
    val icon: DrawableResource,
)

private val topLevelNavigationItems = listOf(
    TopLevelNavigationItem(
        destination = AppDestination.Home,
        label = "Home",
        icon = Res.drawable.ic_home,
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Projects,
        label = "Projects",
        icon = Res.drawable.ic_projects,
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Experience,
        label = "Experience",
        icon = Res.drawable.ic_experience,
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Skills,
        label = "Skills",
        icon = Res.drawable.ic_skills,
    ),
    TopLevelNavigationItem(
        destination = AppDestination.Contact,
        label = "Contact",
        icon = Res.drawable.ic_contact,
    ),
)

@Composable
fun AppNavigationBar(
    currentDestination: AppDestination,
    onDestinationSelected: (AppDestination) -> Unit,
) {
    NavigationBar(
        modifier = Modifier.navigationBarsPadding(),
        containerColor = MaterialTheme.colorScheme.surface,
        tonalElevation = 4.dp,
    ) {
        topLevelNavigationItems.forEach { item ->
            val selected = currentDestination == item.destination

            val iconScale by animateFloatAsState(
                targetValue = if (selected) 1.12f else 1f,
                animationSpec = spring(
                    dampingRatio = 0.7f,
                    stiffness = 500f,
                ),
                label = "${item.label}IconScale",
            )

            val iconTint by animateColorAsState(
                targetValue = if (selected) {
                    MaterialTheme.colorScheme.onSecondaryContainer
                } else {
                    MaterialTheme.colorScheme.onSurfaceVariant
                },
                animationSpec = spring(
                    dampingRatio = 0.9f,
                    stiffness = 450f,
                ),
                label = "${item.label}IconTint",
            )

            NavigationBarItem(
                selected = selected,
                onClick = {
                    onDestinationSelected(item.destination)
                },
                icon = {
                    Icon(
                        painter = painterResource(item.icon),
                        contentDescription = item.label,
                        tint = iconTint,
                        modifier = Modifier.graphicsLayer {
                            scaleX = iconScale
                            scaleY = iconScale
                        },
                    )
                },
                label = {
                    Text(
                        text = item.label,
                        style = MaterialTheme.typography.labelMedium,
                    )
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor =
                        MaterialTheme.colorScheme.onSecondaryContainer,
                    selectedTextColor =
                        MaterialTheme.colorScheme.onSurface,
                    indicatorColor =
                        MaterialTheme.colorScheme.secondaryContainer,
                    unselectedIconColor =
                        MaterialTheme.colorScheme.onSurfaceVariant,
                    unselectedTextColor =
                        MaterialTheme.colorScheme.onSurfaceVariant,
                ),
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
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
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