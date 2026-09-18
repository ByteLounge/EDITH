package com.edith.app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.core.content.ContextCompat
import com.edith.app.data.model.*
import com.edith.app.ui.components.ConfirmationDialog
import com.edith.app.ui.navigation.EdithBottomNavigation
import com.edith.app.ui.navigation.Screen
import com.edith.app.ui.screens.activity.ActivityScreen
import com.edith.app.ui.screens.devices.DevicesScreen
import com.edith.app.ui.screens.home.HomeScreen
import com.edith.app.ui.screens.settings.SettingsScreen
import com.edith.app.ui.screens.voice.VoiceAssistantScreen
import com.edith.app.ui.theme.EDITHTheme
import com.edith.app.ui.theme.EdithBlack
import com.edith.app.ui.theme.EdithCyan
import com.edith.app.ui.theme.EdithSurface
import com.edith.app.ui.theme.EdithSurfaceVariant
import com.edith.app.ui.theme.EdithWhite
import com.edith.app.voice.SpeechRecognizerManager
import com.edith.app.voice.TextToSpeechManager
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private lateinit var speechManager: SpeechRecognizerManager
    private lateinit var ttsManager: TextToSpeechManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val app = application as EdithApplication
        val storage = app.secureStorage
        val apiService = app.apiService

        speechManager = SpeechRecognizerManager(this)
        ttsManager = TextToSpeechManager(this, storage)

        setContent {
            EDITHTheme {
                val coroutineScope = rememberCoroutineScope()
                var currentRoute by remember { mutableStateOf(Screen.Home.route) }

                // State
                var devices by remember { mutableStateOf<List<DeviceItem>>(emptyList()) }
                var history by remember { mutableStateOf<List<CommandHistoryItem>>(emptyList()) }
                var pairingCode by remember { mutableStateOf<String?>(null) }
                var isRefreshing by remember { mutableStateOf(false) }

                // Voice / Command State
                val isListening by speechManager.isListening.collectAsState()
                val liveTranscript by speechManager.transcript.collectAsState()
                var latestCommand by remember { mutableStateOf<String?>(null) }
                var latestResponse by remember { mutableStateOf<String?>(null) }
                var speechResponseText by remember { mutableStateOf<String?>(null) }
                var isCommandProcessing by remember { mutableStateOf(false) }

                // Confirmation State
                var pendingConfirmationToken by remember { mutableStateOf<String?>(null) }
                var pendingConfirmationPrompt by remember { mutableStateOf<String?>(null) }

                // Auth dialog state
                var showAuthDialog by remember { mutableStateOf(!storage.isLoggedIn()) }
                var authEmail by remember { mutableStateOf("") }
                var authPassword by remember { mutableStateOf("") }
                var authIsRegister by remember { mutableStateOf(false) }

                // Permission Launcher
                val permissionLauncher = rememberLauncherForActivityResult(
                    ActivityResultContracts.RequestPermission()
                ) { isGranted ->
                    if (isGranted) {
                        speechManager.startListening()
                    } else {
                        Toast.makeText(this, "Microphone permission required for voice commands", Toast.LENGTH_LONG).show()
                    }
                }

                fun checkMicAndListen() {
                    if (isListening) {
                        speechManager.stopListening()
                    } else {
                        val hasPermission = ContextCompat.checkSelfPermission(
                            this, Manifest.permission.RECORD_AUDIO
                        ) == PackageManager.PERMISSION_GRANTED

                        if (hasPermission) {
                            speechManager.startListening()
                        } else {
                            permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                        }
                    }
                }

                fun refreshData() {
                    if (!storage.isLoggedIn()) return
                    coroutineScope.launch {
                        isRefreshing = true
                        apiService.getDevices().onSuccess { devices = it }
                        apiService.getCommandHistory().onSuccess { history = it }
                        isRefreshing = false
                    }
                }

                fun sendCommand(query: String) {
                    if (query.isBlank()) return
                    latestCommand = query
                    isCommandProcessing = true
                    coroutineScope.launch {
                        apiService.processCommand(query).onSuccess { resp ->
                            isCommandProcessing = false
                            latestResponse = resp.textResponse
                            speechResponseText = resp.speechResponse

                            if (resp.requiresConfirmation && resp.confirmationToken != null) {
                                pendingConfirmationToken = resp.confirmationToken
                                pendingConfirmationPrompt = resp.confirmationPrompt
                            }

                            // Speak response if auto-speak is enabled
                            ttsManager.speak(resp.speechResponse)
                            refreshData()
                        }.onFailure { err ->
                            isCommandProcessing = false
                            val errMessage = "Error: ${err.message ?: "Failed to execute command"}"
                            latestResponse = errMessage
                            ttsManager.speak(errMessage)
                        }
                    }
                }

                // Attach speech callback
                speechManager.onResultCallback = { recognizedText ->
                    sendCommand(recognizedText)
                }

                // Initial load
                LaunchedEffect(storage.isLoggedIn()) {
                    if (storage.isLoggedIn()) {
                        refreshData()
                    }
                }

                Scaffold(
                    bottomBar = {
                        EdithBottomNavigation(
                            currentRoute = currentRoute,
                            onNavigate = { currentRoute = it }
                        )
                    },
                    containerColor = EdithBlack
                ) { paddingValues ->
                    Box(modifier = Modifier.padding(paddingValues)) {
                        when (currentRoute) {
                            Screen.Home.route -> HomeScreen(
                                devices = devices,
                                isListening = isListening,
                                recentCommand = latestCommand,
                                lastResponse = latestResponse,
                                onMicClick = { checkMicAndListen() },
                                onNavigateToVoice = { currentRoute = Screen.Voice.route },
                                onQuickCommand = { cmd -> sendCommand(cmd) }
                            )
                            Screen.Voice.route -> VoiceAssistantScreen(
                                isListening = isListening,
                                transcript = liveTranscript,
                                responseText = latestResponse,
                                speechText = speechResponseText,
                                isLoading = isCommandProcessing,
                                onMicClick = { checkMicAndListen() },
                                onSendText = { text -> sendCommand(text) },
                                onReplaySpeech = { speechResponseText?.let { ttsManager.speak(it, overrideEnabledCheck = true) } }
                            )
                            Screen.Devices.route -> DevicesScreen(
                                devices = devices,
                                isRefreshing = isRefreshing,
                                pairingCode = pairingCode,
                                onRefresh = { refreshData() },
                                onRequestPairingCode = {
                                    coroutineScope.launch {
                                        apiService.generatePairingCode().onSuccess { pairingCode = it.pairingCode }
                                    }
                                },
                                onDismissPairingCode = { pairingCode = null },
                                onRenameDevice = { id, name ->
                                    coroutineScope.launch {
                                        apiService.renameDevice(id, name).onSuccess { refreshData() }
                                    }
                                },
                                onDeleteDevice = { id ->
                                    coroutineScope.launch {
                                        apiService.deleteDevice(id).onSuccess { refreshData() }
                                    }
                                }
                            )
                            Screen.Activity.route -> ActivityScreen(
                                history = history,
                                onClearHistory = {
                                    coroutineScope.launch {
                                        apiService.clearHistory().onSuccess { history = emptyList() }
                                    }
                                }
                            )
                            Screen.Settings.route -> SettingsScreen(
                                storage = storage,
                                onLogout = {
                                    storage.clearSession()
                                    showAuthDialog = true
                                }
                            )
                        }

                        // High-Risk Confirmation Dialog
                        if (pendingConfirmationToken != null && pendingConfirmationPrompt != null) {
                            ConfirmationDialog(
                                prompt = pendingConfirmationPrompt!!,
                                onConfirm = {
                                    val token = pendingConfirmationToken!!
                                    pendingConfirmationToken = null
                                    pendingConfirmationPrompt = null
                                    coroutineScope.launch {
                                        apiService.confirmCommand(token, true).onSuccess { res ->
                                            latestResponse = res.textResponse
                                            ttsManager.speak(res.speechResponse)
                                            refreshData()
                                        }
                                    }
                                },
                                onDismiss = {
                                    val token = pendingConfirmationToken!!
                                    pendingConfirmationToken = null
                                    pendingConfirmationPrompt = null
                                    coroutineScope.launch {
                                        apiService.confirmCommand(token, false)
                                    }
                                }
                            )
                        }

                        // Login / Register Dialog
                        if (showAuthDialog) {
                            Dialog(onDismissRequest = {}) {
                                Surface(
                                    shape = RoundedCornerShape(20.dp),
                                    color = EdithSurface,
                                    modifier = Modifier.fillMaxWidth().border(1.dp, EdithSurfaceVariant, RoundedCornerShape(20.dp))
                                ) {
                                    Column(modifier = Modifier.padding(24.dp)) {
                                        Text(
                                            text = if (authIsRegister) "Create EDITH Account" else "Welcome to EDITH",
                                            style = MaterialTheme.typography.titleLarge,
                                            color = EdithWhite
                                        )
                                        Spacer(modifier = Modifier.height(16.dp))

                                        TextField(
                                            value = authEmail,
                                            onValueChange = { authEmail = it },
                                            label = { Text("Email") },
                                            modifier = Modifier.fillMaxWidth()
                                        )

                                        Spacer(modifier = Modifier.height(12.dp))

                                        TextField(
                                            value = authPassword,
                                            onValueChange = { authPassword = it },
                                            label = { Text("Password") },
                                            modifier = Modifier.fillMaxWidth()
                                        )

                                        Spacer(modifier = Modifier.height(20.dp))

                                        Button(
                                            onClick = {
                                                coroutineScope.launch {
                                                    val res = if (authIsRegister) {
                                                        apiService.register(RegisterRequest(authEmail, authPassword))
                                                    } else {
                                                        apiService.login(LoginRequest(authEmail, authPassword))
                                                    }
                                                    res.onSuccess {
                                                        showAuthDialog = false
                                                        refreshData()
                                                    }.onFailure {
                                                        Toast.makeText(this@MainActivity, it.message ?: "Auth failed", Toast.LENGTH_SHORT).show()
                                                    }
                                                }
                                            },
                                            modifier = Modifier.fillMaxWidth(),
                                            colors = ButtonDefaults.buttonColors(containerColor = EdithCyan)
                                        ) {
                                            Text(if (authIsRegister) "Register" else "Login", color = EdithBlack)
                                        }

                                        Spacer(modifier = Modifier.height(8.dp))

                                        TextButton(
                                            onClick = { authIsRegister = !authIsRegister },
                                            modifier = Modifier.fillMaxWidth()
                                        ) {
                                            Text(
                                                if (authIsRegister) "Already have an account? Log In" else "New to EDITH? Register",
                                                color = EdithCyan
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        speechManager.destroy()
        ttsManager.shutdown()
        super.onDestroy()
    }
}
