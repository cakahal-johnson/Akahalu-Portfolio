package com.akahalu.portfolio.core.network

sealed class NetworkException(
    message: String,
    cause: Throwable? = null,
) : Exception(message, cause) {

    class RequestFailed(
        message: String,
        cause: Throwable? = null,
    ) : NetworkException(message, cause)

    class InvalidResponse(
        message: String,
        cause: Throwable? = null,
    ) : NetworkException(message, cause)

    class SerializationFailed(
        message: String,
        cause: Throwable? = null,
    ) : NetworkException(message, cause)

    class Unknown(
        message: String,
        cause: Throwable? = null,
    ) : NetworkException(message, cause)
}