package com.edith.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class DeviceItem(
    @SerialName("device_id") val deviceId: String,
    @SerialName("owner_id") val ownerId: String,
    val name: String,
    val type: String,
    val platform: String,
    val status: String, // online, offline, connecting
    @SerialName("last_seen") val lastSeen: String,
    val capabilities: List<String> = emptyList(),
    val version: String = "1.0.0"
)

@Serializable
data class PairingCodeResponse(
    @SerialName("pairing_code") val pairingCode: String,
    @SerialName("expires_at") val expiresAt: String,
    @SerialName("expires_in_seconds") val expiresInSeconds: Int
)

@Serializable
data class DeviceRenameRequest(
    val name: String
)
