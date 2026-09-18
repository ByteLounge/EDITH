package com.edith.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

private val DarkColorScheme = darkColorScheme(
    primary = EdithPrimary,
    onPrimary = EdithBlack,
    secondary = EdithCyan,
    onSecondary = EdithBlack,
    tertiary = EdithBlue,
    background = EdithBlack,
    onBackground = EdithWhite,
    surface = EdithSurface,
    onSurface = EdithWhite,
    surfaceVariant = EdithSurfaceVariant,
    onSurfaceVariant = EdithTextSecondary,
    error = EdithError,
    onError = EdithWhite
)

private val LightColorScheme = lightColorScheme(
    primary = EdithBlue,
    onPrimary = EdithWhite,
    secondary = EdithCyan,
    onSecondary = EdithBlack,
    tertiary = EdithPrimary,
    background = EdithWhite,
    onBackground = EdithBlack,
    surface = EdithWhite,
    onSurface = EdithBlack,
    surfaceVariant = EdithWhite,
    onSurfaceVariant = EdithTextMuted,
    error = EdithError,
    onError = EdithWhite
)

@Composable
fun EDITHTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else DarkColorScheme // Dark-first aesthetic

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
