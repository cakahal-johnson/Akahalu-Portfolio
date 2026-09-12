package com.akahalu.portfolio.data.portfolio.cache

import kotlin.time.Clock
import kotlin.time.Duration
import kotlin.time.Duration.Companion.hours
import kotlin.time.Instant
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

class JsonPortfolioCache(
    private val storage: PortfolioCacheStorage,
    private val json: Json = Json {
        ignoreUnknownKeys = true
        encodeDefaults = true
    },
    private val staleDuration: Duration = 24.hours,
    private val clock: Clock = Clock.System,
) {

    suspend fun <T> get(
        key: String,
        serializer: KSerializer<T>,
    ): T? {
        val rawValue = storage.read(key)
            ?: return null

        return runCatching {
            val entry = json.decodeFromString(
                CachedPortfolioEntry.serializer(),
                rawValue,
            )

            val cachedAt = Instant.parse(entry.cachedAt)
            val age = clock.now() - cachedAt

            if (age > staleDuration) {
                storage.remove(key)
                return null
            }

            json.decodeFromString(
                serializer,
                entry.value,
            )
        }.getOrElse {
            storage.remove(key)
            null
        }
    }

    suspend fun <T> save(
        key: String,
        value: T,
        serializer: KSerializer<T>,
    ) {
        val entry = CachedPortfolioEntry(
            cachedAt = clock.now().toString(),
            value = json.encodeToString(
                serializer,
                value,
            ),
        )

        storage.write(
            key = key,
            value = json.encodeToString(
                CachedPortfolioEntry.serializer(),
                entry,
            ),
        )
    }

    suspend fun remove(
        key: String,
    ) {
        storage.remove(key)
    }

    suspend fun clear() {
        storage.clear()
    }

    @Serializable
    private data class CachedPortfolioEntry(
        val cachedAt: String,
        val value: String,
    )
}