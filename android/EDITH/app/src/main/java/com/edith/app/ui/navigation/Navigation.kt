package com.edith.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.vector.ImageVector
import com.edith.app.ui.theme.*

sealed class Screen(val route: String, val title: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Default.Home)
    object Voice : Screen("voice", "Assistant", Icons.Default.Mic)
    object Devices : Screen("devices", "Devices", Icons.Default.Devices)
    object Activity : Screen("activity", "Activity", Icons.Default.History)
    object Settings : Screen("settings", "Settings", Icons.Default.Settings)
}

val bottomNavScreens = listOf(
    Screen.Home,
    Screen.Voice,
    Screen.Devices,
    Screen.Activity,
    Screen.Settings
)

@Composable
fun EdithBottomNavigation(
    currentRoute: String,
    onNavigate: (String) -> Unit
) {
    NavigationBar(
        containerColor = EdithSurface,
        contentColor = EdithWhite
    ) {
        bottomNavScreens.forEach { screen ->
            val selected = currentRoute == screen.route
            NavigationBarItem(
                icon = { Icon(screen.icon, contentDescription = screen.title) },
                label = { Text(screen.title) },
                selected = selected,
                onClick = { onNavigate(screen.route) },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = EdithBlack,
                    selectedTextColor = EdithCyan,
                    indicatorColor = EdithCyan,
                    unselectedIconColor = EdithTextMuted,
                    unselectedTextColor = EdithTextMuted
                )
            )
        }
    }
}
