package com.akahalu.portfolio.data.portfolio.cache

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlinx.coroutines.test.runTest
import kotlinx.serialization.Serializable

class JsonPortfolioCacheTest {

    @Test
    fun savesAndReadsSerializableValue() = runTest {
        val storage = InMemoryPortfolioCacheStorage()
        val cache = JsonPortfolioCache(
            storage = storage,
        )

        val value = TestValue(
            name = "Akahalu",
            count = 5,
        )

        cache.save(
            key = "test",
            value = value,
            serializer = TestValue.serializer(),
        )

        val restored = cache.get(
            key = "test",
            serializer = TestValue.serializer(),
        )

        assertEquals(
            expected = value,
            actual = restored,
        )
    }

    @Test
    fun returnsNullForMissingValue() = runTest {
        val storage = InMemoryPortfolioCacheStorage()
        val cache = JsonPortfolioCache(
            storage = storage,
        )

        val result = cache.get(
            key = "missing",
            serializer = TestValue.serializer(),
        )

        assertNull(result)
    }

    @Test
    fun removesCorruptedCacheValue() = runTest {
        val storage = InMemoryPortfolioCacheStorage()

        storage.write(
            key = "corrupt",
            value = "not-valid-json",
        )

        val cache = JsonPortfolioCache(
            storage = storage,
        )

        val result = cache.get(
            key = "corrupt",
            serializer = TestValue.serializer(),
        )

        assertNull(result)
        assertNull(
            storage.read("corrupt"),
        )
    }

    @Serializable
    private data class TestValue(
        val name: String,
        val count: Int,
    )

    private class InMemoryPortfolioCacheStorage :
        PortfolioCacheStorage {

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
}