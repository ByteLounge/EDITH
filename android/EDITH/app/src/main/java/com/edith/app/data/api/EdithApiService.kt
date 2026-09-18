package com.edith.app.data.api

import com.edith.app.data.model.*
import com.edith.app.data.storage.SecureStorage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException

class EdithApiService(private val storage: SecureStorage) {

    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    private val client = OkHttpClient.Builder().build()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private fun baseUrl(): String = storage.backendUrl

    private fun authHeader(): String? = storage.accessToken?.let { "Bearer $it" }

    suspend fun register(req: RegisterRequest): Result<TokenResponse> = withContext(Dispatchers.IO) {
        try {
            val body = json.encodeToString(req).toRequestBody(jsonMediaType)
            val request = Request.Builder()
                .url("${baseUrl()}/api/v1/auth/register")
                .post(body)
                .build()

            client.newCall(request).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    val tokens = json.decodeFromString<TokenResponse>(respBody)
                    storage.accessToken = tokens.accessToken
                    storage.refreshToken = tokens.refreshToken
                    storage.userEmail = tokens.email
                    Result.success(tokens)
                } else {
                    Result.failure(IOException(respBody))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun login(req: LoginRequest): Result<TokenResponse> = withContext(Dispatchers.IO) {
        try {
            val body = json.encodeToString(req).toRequestBody(jsonMediaType)
            val request = Request.Builder()
                .url("${baseUrl()}/api/v1/auth/login")
                .post(body)
                .build()

            client.newCall(request).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    val tokens = json.decodeFromString<TokenResponse>(respBody)
                    storage.accessToken = tokens.accessToken
                    storage.refreshToken = tokens.refreshToken
                    storage.userEmail = tokens.email
                    Result.success(tokens)
                } else {
                    Result.failure(IOException("Invalid credentials"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getDevices(): Result<List<DeviceItem>> = withContext(Dispatchers.IO) {
        try {
            val builder = Request.Builder().url("${baseUrl()}/api/v1/devices")
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Failed to fetch devices: ${response.code}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun generatePairingCode(): Result<PairingCodeResponse> = withContext(Dispatchers.IO) {
        try {
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/devices/pair/code")
                .post("{}".toRequestBody(jsonMediaType))
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Failed to generate pairing code: ${response.code}"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun renameDevice(deviceId: String, newName: String): Result<DeviceItem> = withContext(Dispatchers.IO) {
        try {
            val body = json.encodeToString(DeviceRenameRequest(newName)).toRequestBody(jsonMediaType)
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/devices/$deviceId")
                .patch(body)
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Failed to rename device"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun deleteDevice(deviceId: String): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/devices/$deviceId")
                .delete()
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                if (response.isSuccessful) {
                    Result.success(true)
                } else {
                    Result.failure(IOException("Failed to delete device"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun processCommand(query: String): Result<ProcessCommandResponse> = withContext(Dispatchers.IO) {
        try {
            val body = json.encodeToString(ProcessCommandRequest(query)).toRequestBody(jsonMediaType)
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/commands/process")
                .post(body)
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Failed to process command: $respBody"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun confirmCommand(confirmationToken: String, confirmed: Boolean): Result<ProcessCommandResponse> = withContext(Dispatchers.IO) {
        try {
            val body = json.encodeToString(ConfirmCommandRequest(confirmationToken, confirmed)).toRequestBody(jsonMediaType)
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/commands/confirm")
                .post(body)
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Confirmation failed: $respBody"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getCommandHistory(): Result<List<CommandHistoryItem>> = withContext(Dispatchers.IO) {
        try {
            val builder = Request.Builder().url("${baseUrl()}/api/v1/commands/history")
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                val respBody = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    Result.success(json.decodeFromString(respBody))
                } else {
                    Result.failure(IOException("Failed to fetch history"))
                }
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun clearHistory(): Result<Boolean> = withContext(Dispatchers.IO) {
        try {
            val builder = Request.Builder()
                .url("${baseUrl()}/api/v1/commands/history")
                .delete()
            authHeader()?.let { builder.addHeader("Authorization", it) }

            client.newCall(builder.build()).execute().use { response ->
                Result.success(response.isSuccessful)
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
