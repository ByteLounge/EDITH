package com.edith.app.ui.screens.devices

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import com.edith.app.data.model.DeviceItem
import com.edith.app.ui.components.DeviceCard
import com.edith.app.ui.theme.*

@Composable
fun DevicesScreen(
    devices: List<DeviceItem>,
    isRefreshing: Boolean,
    pairingCode: String?,
    onRefresh: () -> Unit,
    onRequestPairingCode: () -> Unit,
    onDismissPairingCode: () -> Unit,
    onRenameDevice: (String, String) -> Unit,
    onDeleteDevice: (String) -> Unit
) {
    var selectedDeviceForRename by remember { mutableStateOf<DeviceItem?>(null) }
    var newDeviceName by remember { mutableStateOf("") }

    Box(modifier = Modifier.fillMaxSize().background(EdithBlack)) {
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp),
            contentPadding = PaddingValues(top = 24.dp, bottom = 100.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "Devices",
                            style = MaterialTheme.typography.headlineMedium,
                            color = EdithWhite
                        )
                        Text(
                            text = "${devices.size} registered endpoints",
                            style = MaterialTheme.typography.bodyMedium,
                            color = EdithTextSecondary
                        )
                    }

                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        IconButton(onClick = onRefresh) {
                            Icon(Icons.Default.Refresh, contentDescription = "Refresh", tint = EdithTextSecondary)
                        }
                        Button(
                            onClick = onRequestPairingCode,
                            colors = ButtonDefaults.buttonColors(containerColor = EdithCyan),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Icon(Icons.Default.Add, contentDescription = null, tint = EdithBlack)
                            Spacer(modifier = Modifier.width(4.dp))
                            Text("Pair", color = EdithBlack, fontWeight = FontWeight.SemiBold)
                        }
                    }
                }
            }

            if (devices.isEmpty()) {
                item {
                    Surface(
                        shape = RoundedCornerShape(16.dp),
                        color = EdithSurface,
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 20.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(32.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(
                                text = "No Devices Connected",
                                style = MaterialTheme.typography.titleMedium,
                                color = EdithWhite
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Tap 'Pair' above to generate a 6-digit pairing code and connect your Windows laptop.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = EdithTextSecondary
                            )
                        }
                    }
                }
            } else {
                items(devices) { device ->
                    DeviceCard(
                        device = device,
                        onMenuClick = {
                            selectedDeviceForRename = device
                            newDeviceName = device.name
                        }
                    )
                }
            }
        }

        // Pairing Code Dialog
        if (pairingCode != null) {
            Dialog(onDismissRequest = onDismissPairingCode) {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = EdithSurface,
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, EdithCyan.copy(alpha = 0.5f), RoundedCornerShape(20.dp))
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Pair New Device",
                            style = MaterialTheme.typography.titleLarge,
                            color = EdithWhite
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Enter this 6-digit code on your Windows laptop using the EDITH Agent:",
                            style = MaterialTheme.typography.bodyMedium,
                            color = EdithTextSecondary
                        )

                        Spacer(modifier = Modifier.height(20.dp))

                        Surface(
                            shape = RoundedCornerShape(12.dp),
                            color = EdithSurfaceVariant,
                            modifier = Modifier.padding(horizontal = 16.dp)
                        ) {
                            Text(
                                text = pairingCode,
                                style = MaterialTheme.typography.headlineLarge,
                                color = EdithCyan,
                                letterSpacing = 8.sp,
                                modifier = Modifier.padding(horizontal = 24.dp, vertical = 12.dp)
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))
                        Text(
                            text = "Expires in 5 minutes",
                            style = MaterialTheme.typography.labelSmall,
                            color = EdithWarning
                        )

                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = onDismissPairingCode,
                            modifier = Modifier.fillMaxWidth(),
                            colors = ButtonDefaults.buttonColors(containerColor = EdithSurfaceVariant),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("Done", color = EdithWhite)
                        }
                    }
                }
            }
        }

        // Rename Device Dialog
        if (selectedDeviceForRename != null) {
            val dev = selectedDeviceForRename!!
            Dialog(onDismissRequest = { selectedDeviceForRename = null }) {
                Surface(
                    shape = RoundedCornerShape(20.dp),
                    color = EdithSurface,
                    modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(20.dp))
                ) {
                    Column(modifier = Modifier.padding(24.dp)) {
                        Text("Manage Device", style = MaterialTheme.typography.titleLarge, color = EdithWhite)
                        Spacer(modifier = Modifier.height(16.dp))

                        TextField(
                            value = newDeviceName,
                            onValueChange = { newDeviceName = it },
                            label = { Text("Device Name") },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Spacer(modifier = Modifier.height(20.dp))

                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            TextButton(
                                onClick = {
                                    onDeleteDevice(dev.deviceId)
                                    selectedDeviceForRename = null
                                }
                            ) {
                                Text("Revoke", color = EdithError)
                            }

                            Row {
                                TextButton(onClick = { selectedDeviceForRename = null }) {
                                    Text("Cancel", color = EdithTextSecondary)
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                                Button(
                                    onClick = {
                                        onRenameDevice(dev.deviceId, newDeviceName)
                                        selectedDeviceForRename = null
                                    },
                                    colors = ButtonDefaults.buttonColors(containerColor = EdithCyan)
                                ) {
                                    Text("Save", color = EdithBlack)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
