package com.edith.app.ui.screens.voice

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Send
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.edith.app.ui.components.VoiceWaveIndicator
import com.edith.app.ui.theme.*

@Composable
fun VoiceAssistantScreen(
    isListening: Boolean,
    transcript: String,
    responseText: String?,
    speechText: String?,
    isLoading: Boolean,
    onMicClick: () -> Unit,
    onSendText: (String) -> Unit,
    onReplaySpeech: () -> Unit
) {
    var textInput by remember { mutableStateOf("") }
    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EdithBlack)
            .padding(horizontal = 20.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(24.dp))

        // Title
        Text(
            text = "Voice Assistant",
            style = MaterialTheme.typography.headlineMedium,
            color = EdithWhite
        )
        Text(
            text = if (isListening) "Listening to your voice..." else "Ready for command",
            style = MaterialTheme.typography.bodyMedium,
            color = if (isListening) EdithCyan else EdithTextSecondary
        )

        Spacer(modifier = Modifier.height(30.dp))

        // Large Wave Visualizer
        VoiceWaveIndicator(
            isListening = isListening,
            size = 120.dp
        ) {
            IconButton(
                onClick = onMicClick,
                modifier = Modifier
                    .size(110.dp)
                    .clip(CircleShape)
                    .background(if (isListening) EdithCyan else EdithPrimary)
            ) {
                Icon(
                    imageVector = Icons.Default.Mic,
                    contentDescription = "Mic",
                    tint = EdithBlack,
                    modifier = Modifier.size(54.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(30.dp))

        // Transcript & Response Card Area
        Column(
            modifier = Modifier
                .weight(1f)
                .fillMaxWidth()
                .verticalScroll(scrollState),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // User Speech Transcript
            if (transcript.isNotBlank()) {
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = EdithSurfaceVariant,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "YOU SAID",
                            style = MaterialTheme.typography.labelSmall,
                            color = EdithTextMuted
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = "\"$transcript\"",
                            style = MaterialTheme.typography.bodyLarge,
                            color = EdithWhite
                        )
                    }
                }
            }

            // Loading state
            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxWidth(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = EdithCyan, modifier = Modifier.size(32.dp))
                }
            }

            // EDITH Response
            if (!responseText.isNullOrBlank()) {
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = EdithSurface),
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, EdithCyan.copy(alpha = 0.3f), RoundedCornerShape(16.dp))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = "EDITH",
                                style = MaterialTheme.typography.labelSmall,
                                color = EdithCyan
                            )
                            IconButton(onClick = onReplaySpeech) {
                                Icon(
                                    imageVector = Icons.Default.VolumeUp,
                                    contentDescription = "Speak",
                                    tint = EdithCyan
                                )
                            }
                        }
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = responseText,
                            style = MaterialTheme.typography.bodyLarge,
                            color = EdithWhite
                        )
                    }
                }
            }
        }

        // Bottom Text Input Bar (Alternative to Voice)
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            TextField(
                value = textInput,
                onValueChange = { textInput = it },
                placeholder = { Text("Type a command...", color = EdithTextMuted) },
                shape = RoundedCornerShape(24.dp),
                colors = TextFieldDefaults.colors(
                    focusedContainerColor = EdithSurface,
                    unfocusedContainerColor = EdithSurface,
                    focusedIndicatorColor = Color.Transparent,
                    unfocusedIndicatorColor = Color.Transparent,
                    focusedTextColor = EdithWhite,
                    unfocusedTextColor = EdithWhite
                ),
                modifier = Modifier
                    .weight(1f)
                    .border(1.dp, EdithSurfaceVariant, RoundedCornerShape(24.dp))
            )

            Spacer(modifier = Modifier.width(8.dp))

            IconButton(
                onClick = {
                    if (textInput.isNotBlank()) {
                        onSendText(textInput)
                        textInput = ""
                    }
                },
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(EdithPrimary)
            ) {
                Icon(
                    imageVector = Icons.Default.Send,
                    contentDescription = "Send",
                    tint = EdithBlack
                )
            }
        }
    }
}
