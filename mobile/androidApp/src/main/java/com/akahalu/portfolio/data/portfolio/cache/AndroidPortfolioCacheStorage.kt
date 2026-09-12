package com.akahalu.portfolio.data.portfolio.cache

import android.content.Context
import java.io.File

class AndroidPortfolioCacheStorage(
    context: Context,
) : PortfolioCacheStorage {

    private val cacheDirectory: File =
        File(
            context.cacheDir,
            CACHE_DIRECTORY_NAME,
        ).apply {
            mkdirs()
        }

    override suspend fun read(
        key: String,
    ): String? {
        val file = fileForKey(key)

        if (!file.exists()) {
            return null
        }

        return runCatching {
            file.readText()
        }.getOrNull()
    }

    override suspend fun write(
        key: String,
        value: String,
    ) {
        runCatching {
            fileForKey(key).writeText(value)
        }
    }

    override suspend fun remove(
        key: String,
    ) {
        runCatching {
            fileForKey(key).delete()
        }
    }

    override suspend fun clear() {
        runCatching {
            cacheDirectory
                .listFiles()
                ?.forEach { file ->
                    file.delete()
                }
        }
    }

    private fun fileForKey(
        key: String,
    ): File {
        return File(
            cacheDirectory,
            encodeKey(key),
        )
    }

    private fun encodeKey(
        key: String,
    ): String {
        return key
            .encodeToByteArray()
            .joinToString(separator = "") { byte ->
                byte
                    .toInt()
                    .and(0xFF)
                    .toString(16)
                    .padStart(2, '0')
            }
    }

    private companion object {
        const val CACHE_DIRECTORY_NAME = "portfolio_cache"
    }
}