package com.akahalu.portfolio

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.akahalu.portfolio.core.network.NetworkConfig

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val networkConfig = NetworkConfig(
            baseUrl = "http://10.0.2.2:8000/api/v1/",
        )

        setContent {
            App(
                networkConfig = networkConfig,
            )
        }
    }
}