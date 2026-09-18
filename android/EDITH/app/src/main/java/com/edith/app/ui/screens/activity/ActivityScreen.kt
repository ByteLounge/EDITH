package com.edith.app.ui.screens.activity

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.History
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.edith.app.data.model.CommandHistoryItem
import com.edith.app.ui.theme.*

@Composable
fun ActivityScreen(
    history: List<CommandHistoryItem>,
    onClearHistory: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EdithBlack)
            .padding(horizontal = 20.dp)
    ) {
        Spacer(modifier = Modifier.height(24.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Activity Log",
                    style = MaterialTheme.typography.headlineMedium,
                    color = EdithWhite
                )
                Text(
                    text = "${history.size} recorded commands",
                    style = MaterialTheme.typography.bodyMedium,
                    color = EdithTextSecondary
                )
            }

            if (history.isNotEmpty()) {
                IconButton(onClick = onClearHistory) {
                    Icon(
                        imageVector = Icons.Default.Delete,
                        contentDescription = "Clear History",
                        tint = EdithTextMuted
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        if (history.isEmpty()) {
            Surface(
                shape = RoundedCornerShape(16.dp),
                color = EdithSurface,
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Icon(
                        imageVector = Icons.Default.History,
                        contentDescription = null,
                        tint = EdithTextMuted,
                        modifier = Modifier.size(48.dp)
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "No Activity Recorded",
                        style = MaterialTheme.typography.titleMedium,
                        color = EdithWhite
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Your voice and text command logs will appear here.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = EdithTextSecondary
                    )
                }
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(bottom = 100.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(history) { item ->
                    HistoryCard(item)
                }
            }
        }
    }
}

@Composable
fun HistoryCard(item: CommandHistoryItem) {
    val isSuccess = item.status.lowercase() == "completed"
    val statusColor = if (isSuccess) EdithSuccess else EdithError

    Card(
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = EdithSurface),
        modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, EdithSurfaceVariant, RoundedCornerShape(14.dp))
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isSuccess) Icons.Default.CheckCircle else Icons.Default.Error,
                contentDescription = item.status,
                tint = statusColor,
                modifier = Modifier.size(24.dp)
            )

            Spacer(modifier = Modifier.width(14.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.query,
                    style = MaterialTheme.typography.bodyLarge,
                    color = EdithWhite
                )
                Spacer(modifier = Modifier.height(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = item.deviceName ?: "Core",
                        style = MaterialTheme.typography.labelSmall,
                        color = EdithCyan
                    )
                    if (item.action != null) {
                        Text(
                            text = " • ${item.action}",
                            style = MaterialTheme.typography.labelSmall,
                            color = EdithTextSecondary
                        )
                    }
                }
            }

            Text(
                text = item.createdAt.take(10),
                style = MaterialTheme.typography.labelSmall,
                color = EdithTextMuted,
                fontSize = 10.sp
            )
        }
    }
}
