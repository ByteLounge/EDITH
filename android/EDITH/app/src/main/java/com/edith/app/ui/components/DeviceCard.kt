package com.edith.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Computer
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.PhoneAndroid
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.edith.app.data.model.DeviceItem
import com.edith.app.ui.theme.*

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun DeviceCard(
    device: DeviceItem,
    onMenuClick: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val isOnline = device.status.lowercase() == "online"
    val statusColor = when (device.status.lowercase()) {
        "online" -> EdithSuccess
        "connecting" -> EdithWarning
        else -> EdithTextMuted
    }

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = EdithSurface),
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, EdithSurfaceVariant, RoundedCornerShape(16.dp))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        contentAlignment = Alignment.Center,
                        modifier = Modifier
                            .size(44.dp)
                            .clip(RoundedCornerShape(12.dp))
                            .background(EdithSurfaceVariant)
                    ) {
                        Icon(
                            imageVector = if (device.platform.lowercase() == "android" || device.type == "phone")
                                Icons.Default.PhoneAndroid else Icons.Default.Computer,
                            contentDescription = device.platform,
                            tint = if (isOnline) EdithCyan else EdithTextMuted
                        )
                    }

                    Spacer(modifier = Modifier.width(12.dp))

                    Column {
                        Text(
                            text = device.name,
                            style = MaterialTheme.typography.titleMedium,
                            color = EdithWhite
                        )
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(8.dp)
                                    .clip(CircleShape)
                                    .background(statusColor)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "${device.platform.replaceFirstChar { it.uppercase() }} • ${device.status.uppercase()}",
                                style = MaterialTheme.typography.labelSmall,
                                color = statusColor
                            )
                        }
                    }
                }

                IconButton(onClick = onMenuClick) {
                    Icon(
                        imageVector = Icons.Default.MoreVert,
                        contentDescription = "Options",
                        tint = EdithTextSecondary
                    )
                }
            }

            if (device.capabilities.isNotEmpty()) {
                Spacer(modifier = Modifier.height(12.dp))
                HorizontalDivider(color = EdithSurfaceVariant, thickness = 0.8.dp)
                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = "CAPABILITIES",
                    style = MaterialTheme.typography.labelSmall,
                    color = EdithTextMuted,
                    fontSize = 10.sp
                )

                Spacer(modifier = Modifier.height(6.dp))

                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    verticalArrangement = Arrangement.spacedBy(6.dp)
                ) {
                    device.capabilities.take(8).forEach { cap ->
                        CapabilityBadge(cap)
                    }
                    if (device.capabilities.size > 8) {
                        CapabilityBadge("+${device.capabilities.size - 8} more")
                    }
                }
            }
        }
    }
}

@Composable
fun CapabilityBadge(name: String) {
    val cleanName = name.replace("_", " ").split(" ").joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } }
    Surface(
        shape = RoundedCornerShape(8.dp),
        color = EdithSurfaceVariant
    ) {
        Text(
            text = cleanName,
            style = MaterialTheme.typography.labelSmall,
            color = EdithCyan,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
        )
    }
}
