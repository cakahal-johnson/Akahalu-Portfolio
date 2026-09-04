package com.akahalu.portfolio

import kotlin.test.Test
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class PlatformTest {

    @Test
    fun platformNameIsNotBlank() {
        assertTrue(getPlatform().name.isNotBlank())
    }

    @Test
    fun platformIsAvailable() {
        assertNotNull(getPlatform())
    }
}