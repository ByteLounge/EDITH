package com.edith.app.ui.screens.settings

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Logout
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.edith.app.data.storage.SecureStorage
import com.edith.app.ui.theme.*

@Composable
fun SettingsScreen(
    storage: SecureStorage,
    onLogout: () -> Unit
) {
    var ttsEnabled by remember { mutableStateOf(storage.ttsEnabled) }
    var autoSpeak by remember { mutableStateOf(storage.autoSpeak) }
    var speechRate by remember { mutableFloatStateOf(storage.speechRate) }
    var historyEnabled by remember { mutableStateOf(storage.historyEnabled) }
    var backendUrl by remember { mutableStateOf(storage.backendUrl) }

    val scrollState = rememberScrollState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EdithBlack)
            .padding(horizontal = 20.dp)
            .verticalScroll(scrollState)
    ) {
        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "Settings",
            style = MaterialTheme.typography.headlineMedium,
            color = EdithWhite
        )
        Text(
            text = "Configure voice, AI provider, and privacy",
            style = MaterialTheme.typography.bodyMedium,
            color = EdithTextSecondary
        )

        Spacer(modifier = Modifier.height(24.dp))

        // VOICE SETTINGS
        Text("VOICE & SPEECH (TTS)", style = MaterialTheme.typography.labelSmall, color = EdithTextMuted)
        Spacer(modifier = Modifier.height(8.dp))
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = EdithSurface),
            modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(16.dp))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Spoken Responses (TTS)", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                        Text("Speak responses out loud", style = MaterialTheme.typography.bodyMedium, color = EdithTextSecondary)
                    }
                    Switch(
                        checked = ttsEnabled,
                        onCheckedChange = {
                            ttsEnabled = it
                            storage.ttsEnabled = it
                        }
                    )
                }

                HorizontalDivider(color = EdithSurfaceVariant, modifier = Modifier.padding(vertical = 12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Auto-Speak", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                        Text("Automatically speak when response arrives", style = MaterialTheme.typography.bodyMedium, color = EdithTextSecondary)
                    }
                    Switch(
                        checked = autoSpeak,
                        onCheckedChange = {
                            autoSpeak = it
                            storage.autoSpeak = it
                        }
                    )
                }

                HorizontalDivider(color = EdithSurfaceVariant, modifier = Modifier.padding(vertical = 12.dp))

                Text("Speech Rate: ${String.format("%.1fx", speechRate)}", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                Slider(
                    value = speechRate,
                    onValueChange = {
                        speechRate = it
                        storage.speechRate = it
                    },
                    valueRange = 0.5f..2.0f,
                    steps = 5,
                    colors = SliderDefaults.colors(thumbColor = EdithCyan, activeTrackColor = EdithCyan)
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // AI PROVIDER SETTINGS
        Text("AI ENGINE", style = MaterialTheme.typography.labelSmall, color = EdithTextMuted)
        Spacer(modifier = Modifier.height(8.dp))
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = EdithSurface),
            modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(16.dp))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Active Engine: Ollama (Local)", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    "Ollama coordinates natural language parsing into strictly defined capability tools.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = EdithTextSecondary
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // NETWORK SETTINGS
        Text("BACKEND CONNECTION", style = MaterialTheme.typography.labelSmall, color = EdithTextMuted)
        Spacer(modifier = Modifier.height(8.dp))
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = EdithSurface),
            modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(16.dp))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text("Server Host URL", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                Spacer(modifier = Modifier.height(8.dp))
                TextField(
                    value = backendUrl,
                    onValueChange = {
                        backendUrl = it
                        storage.backendUrl = it
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = TextFieldDefaults.colors(
                        focusedContainerColor = EdithSurfaceVariant,
                        unfocusedContainerColor = EdithSurfaceVariant,
                        focusedTextColor = EdithWhite,
                        unfocusedTextColor = EdithWhite
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // PRIVACY SETTINGS
        Text("PRIVACY & AUDIT", style = MaterialTheme.typography.labelSmall, color = EdithTextMuted)
        Spacer(modifier = Modifier.height(8.dp))
        Card(
            shape = RoundedCornerShape(16.dp),
            colors = CardDefaults.cardColors(containerColor = EdithSurface),
            modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(16.dp))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Record Command History", style = MaterialTheme.typography.bodyLarge, color = EdithWhite)
                        Text("Voice audio is NEVER stored. Transcripts only.", style = MaterialTheme.typography.bodyMedium, color = EdithTextSecondary)
                    }
                    Switch(
                        checked = historyEnabled,
                        onCheckedChange = {
                            historyEnabled = it
                            storage.historyEnabled = it
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // LOGOUT BUTTON
        OutlinedButton(
            onClick = onLogout,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = EdithError),
            shape = RoundedCornerShape(14.dp)
        ) {
            Icon(Icons.Default.Logout, contentDescription = null, tint = EdithError)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Sign Out of EDITH", color = EdithError)
        }

        Spacer(modifier = Modifier.height(100.dp))
    }
}
