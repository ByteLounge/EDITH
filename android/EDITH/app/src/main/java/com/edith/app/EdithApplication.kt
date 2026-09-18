package com.edith.app

import android.app.Application
import com.edith.app.data.api.EdithApiService
import com.edith.app.data.storage.SecureStorage

class EdithApplication : Application() {

    lateinit var secureStorage: SecureStorage
        private set

    lateinit var apiService: EdithApiService
        private set

    override fun onCreate() {
        super.onCreate()
        secureStorage = SecureStorage(this)
        apiService = EdithApiService(secureStorage)
    }
}
