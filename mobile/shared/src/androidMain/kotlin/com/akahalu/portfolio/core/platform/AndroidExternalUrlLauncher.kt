package com.akahalu.portfolio.core.platform

import android.content.Context
import android.content.Intent
import android.net.Uri

class AndroidExternalUrlLauncher(
    private val context: Context,
) : ExternalUrlLauncher {

    override fun openUrl(url: String) {
        val intent = Intent(
            Intent.ACTION_VIEW,
            Uri.parse(url),
        ).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }

        context.startActivity(intent)
    }
}