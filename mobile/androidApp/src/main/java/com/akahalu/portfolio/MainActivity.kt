package com.akahalu.portfolio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.akahalu.portfolio.core.network.NetworkConfig
import com.akahalu.portfolio.core.platform.AndroidExternalUrlLauncher

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val networkConfig = NetworkConfig(
            baseUrl = BuildConfig.API_BASE_URL,
        )

        val externalUrlLauncher = AndroidExternalUrlLauncher(
            context = applicationContext,
        )

        setContent {
            App(
                networkConfig = networkConfig,
                externalUrlLauncher = externalUrlLauncher,
            )
        }
    }
}