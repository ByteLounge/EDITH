package com.edith.app.data.model

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ProcessCommandRequest(
    val query: String
)

@Serializable
data class ProcessCommandResponse(
    @SerialName("command_id") val commandId: String,
    val status: String,
    @SerialName("target_device_id") val targetDeviceId: String? = null,
    val capability: String? = null,
    @SerialName("speech_response") val speechResponse: String,
    @SerialName("text_response") val textResponse: String,
    @SerialName("requires_confirmation") val requiresConfirmation: Boolean = false,
    @SerialName("confirmation_token") val confirmationToken: String? = null,
    @SerialName("confirmation_prompt") val confirmationPrompt: String? = null
)

@Serializable
data class ConfirmCommandRequest(
    @SerialName("confirmation_token") val confirmationToken: String,
    val confirmed: Boolean
)

@Serializable
data class CommandHistoryItem(
    val id: String,
    val query: String,
    val action: String? = null,
    @SerialName("device_name") val deviceName: String? = null,
    val status: String, // completed, failed, cancelled
    @SerialName("created_at") val createdAt: String
)
