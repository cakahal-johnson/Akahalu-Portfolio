package com.akahalu.portfolio.data.portfolio.repository

import com.akahalu.portfolio.data.portfolio.cache.JsonPortfolioCache
import com.akahalu.portfolio.data.portfolio.cache.PortfolioCacheStorage

internal fun createTestPortfolioCache(): JsonPortfolioCache {
    return JsonPortfolioCache(
        storage = InMemoryPortfolioCacheStorage(),
    )
}

private class InMemoryPortfolioCacheStorage : PortfolioCacheStorage {

    private val values = mutableMapOf<String, String>()

    override suspend fun read(
        key: String,
    ): String? {
        return values[key]
    }

    override suspend fun write(
        key: String,
        value: String,
    ) {
        values[key] = value
    }

    override suspend fun remove(
        key: String,
    ) {
        values.remove(key)
    }

    override suspend fun clear() {
        values.clear()
    }
}
