package com.edith.app.voice

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import com.edith.app.data.storage.SecureStorage
import java.util.Locale

class TextToSpeechManager(
    context: Context,
    private val storage: SecureStorage
) : TextToSpeech.OnInitListener {

    private var tts: TextToSpeech? = TextToSpeech(context, this)
    private var isInitialized = false

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts?.setLanguage(Locale.US)
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Log.w("EDITH_TTS", "US English TTS language not supported or missing data.")
            } else {
                isInitialized = true
                tts?.setSpeechRate(storage.speechRate)
            }
        } else {
            Log.e("EDITH_TTS", "TTS Initialization failed: $status")
        }
    }

    fun speak(text: String, overrideEnabledCheck: Boolean = false) {
        if (!storage.ttsEnabled && !overrideEnabledCheck) return
        if (!isInitialized) return

        tts?.setSpeechRate(storage.speechRate)
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "edith_tts_utterance")
    }

    fun stop() {
        tts?.stop()
    }

    fun shutdown() {
        tts?.stop()
        tts?.shutdown()
        tts = null
        isInitialized = false
    }
}
