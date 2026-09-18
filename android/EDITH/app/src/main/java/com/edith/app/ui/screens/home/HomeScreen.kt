package com.edith.app.ui.screens.home

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.MicOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.edith.app.data.model.DeviceItem
import com.edith.app.ui.components.DeviceCard
import com.edith.app.ui.components.VoiceWaveIndicator
import com.edith.app.ui.theme.*

@Composable
fun HomeScreen(
    devices: List<DeviceItem>,
    isListening: Boolean,
    recentCommand: String?,
    lastResponse: String?,
    onMicClick: () -> Unit,
    onNavigateToVoice: () -> Unit,
    onQuickCommand: (String) -> Unit
) {
    val onlineCount = devices.count { it.status.lowercase() == "online" }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(EdithBlack)
            .padding(horizontal = 20.dp),
        contentPadding = PaddingValues(top = 24.dp, bottom = 100.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        // Header
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = "EDITH",
                        style = MaterialTheme.typography.headlineLarge,
                        color = EdithCyan,
                        letterSpacing = 2.sp
                    )
                    Text(
                        text = "Autonomous Device Coordinator",
                        style = MaterialTheme.typography.labelSmall,
                        color = EdithTextMuted
                    )
                }

                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = EdithSurfaceVariant,
                    modifier = Modifier.border(1.dp, EdithSurfaceLight, RoundedCornerShape(20.dp))
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(8.dp)
                                .clip(CircleShape)
                                .background(if (onlineCount > 0) EdithSuccess else EdithTextMuted)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "$onlineCount/${devices.size} Online",
                            style = MaterialTheme.typography.labelSmall,
                            color = EdithWhite
                        )
                    }
                }
            }
        }

        // Voice Action Center
        item {
            Card(
                shape = RoundedCornerShape(24.dp),
                colors = CardDefaults.cardColors(containerColor = EdithSurface),
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, EdithSurfaceVariant, RoundedCornerShape(24.dp))
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(24.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = if (isListening) "Listening..." else "How can I help?",
                        style = MaterialTheme.typography.titleLarge,
                        color = EdithWhite
                    )

                    Spacer(modifier = Modifier.height(6.dp))

                    Text(
                        text = if (isListening) "Speak your command clearly" else "Tap microphone or say a command",
                        style = MaterialTheme.typography.bodyMedium,
                        color = EdithTextSecondary
                    )

                    Spacer(modifier = Modifier.height(20.dp))

                    VoiceWaveIndicator(isListening = isListening, size = 84.dp) {
                        IconButton(
                            onClick = onMicClick,
                            modifier = Modifier
                                .size(84.dp)
                                .clip(CircleShape)
                                .background(if (isListening) EdithCyan else EdithPrimary)
                        ) {
                            Icon(
                                imageVector = if (isListening) Icons.Default.Mic else Icons.Default.Mic,
                                contentDescription = "Microphone",
                                tint = EdithBlack,
                                modifier = Modifier.size(40.dp)
                            )
                        }
                    }

                    if (!lastResponse.isNullOrBlank()) {
                        Spacer(modifier = Modifier.height(20.dp))
                        Surface(
                            shape = RoundedCornerShape(14.dp),
                            color = EdithSurfaceVariant,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text(
                                text = lastResponse,
                                style = MaterialTheme.typography.bodyMedium,
                                color = EdithCyan,
                                modifier = Modifier.padding(14.dp)
                            )
                        }
                    }
                }
            }
        }

        // Quick Suggestions
        item {
            Text(
                text = "SUGGESTED ACTIONS",
                style = MaterialTheme.typography.labelSmall,
                color = EdithTextMuted
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                SuggestionChip(
                    onClick = { onQuickCommand("What's my laptop battery?") },
                    label = { Text("Laptop Battery", color = EdithWhite, fontSize = 12.sp) },
                    colors = SuggestionChipDefaults.suggestionChipColors(containerColor = EdithSurfaceVariant),
                    border = null
                )
                SuggestionChip(
                    onClick = { onQuickCommand("Open VS Code on my laptop") },
                    label = { Text("Open VS Code", color = EdithWhite, fontSize = 12.sp) },
                    colors = SuggestionChipDefaults.suggestionChipColors(containerColor = EdithSurfaceVariant),
                    border = null
                )
                SuggestionChip(
                    onClick = { onQuickCommand("Lock my laptop") },
                    label = { Text("Lock Laptop", color = EdithWhite, fontSize = 12.sp) },
                    colors = SuggestionChipDefaults.suggestionChipColors(containerColor = EdithSurfaceVariant),
                    border = null
                )
            }
        }

        // Connected Devices Header
        item {
            Text(
                text = "CONNECTED DEVICES",
                style = MaterialTheme.typography.labelSmall,
                color = EdithTextMuted
            )
        }

        // Devices List
        if (devices.isEmpty()) {
            item {
                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = EdithSurface,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Box(modifier = Modifier.padding(24.dp), contentAlignment = Alignment.Center) {
                        Text(
                            text = "No devices connected yet. Pair your laptop in Devices.",
                            style = MaterialTheme.typography.bodyMedium,
                            color = EdithTextSecondary
                        )
                    }
                }
            }
        } else {
            items(devices) { device ->
                DeviceCard(device = device)
            }
        }
    }
}
