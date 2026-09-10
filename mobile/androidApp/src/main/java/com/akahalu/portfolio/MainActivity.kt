package com.akahalu.portfolio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.akahalu.portfolio.core.network.NetworkConfig

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val networkConfig = NetworkConfig(
            baseUrl = BuildConfig.API_BASE_URL,
        )

        setContent {
            App(
                networkConfig = networkConfig,
            )
        }
    }
}