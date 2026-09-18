package com.edith.app.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.edith.app.ui.theme.EdithCyan
import com.edith.app.ui.theme.EdithPrimary

@Composable
fun VoiceWaveIndicator(
    isListening: Boolean,
    rmsLevel: Float = 0f,
    size: Dp = 100.dp,
    content: @Composable () -> Unit
) {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val pulseScale by infiniteTransition.animateFloat(
        initialValue = 1.0f,
        targetValue = if (isListening) 1.35f else 1.0f,
        animationSpec = infiniteRepeatable(
            animation = tween(900, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulseScale"
    )

    val waveAlpha by infiniteTransition.animateFloat(
        initialValue = if (isListening) 0.35f else 0f,
        targetValue = if (isListening) 0.05f else 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(900, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "waveAlpha"
    )

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.size(size * 1.5f)
    ) {
        if (isListening) {
            // Outer pulsating aura
            Box(
                modifier = Modifier
                    .size(size)
                    .scale(pulseScale)
                    .clip(CircleShape)
                    .background(EdithCyan.copy(alpha = waveAlpha))
            )
            // Mid glow ring
            Box(
                modifier = Modifier
                    .size(size * 1.15f)
                    .clip(CircleShape)
                    .background(EdithPrimary.copy(alpha = 0.15f))
            )
        }

        // Inner microphone content
        content()
    }
}
