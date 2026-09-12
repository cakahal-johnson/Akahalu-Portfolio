package com.akahalu.portfolio.data.portfolio.cache

interface PortfolioCacheStorage {

    suspend fun read(key: String): String?

    suspend fun write(
        key: String,
        value: String,
    )

    suspend fun remove(key: String)

    suspend fun clear()
}