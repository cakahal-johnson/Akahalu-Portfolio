import axios from "axios"

import type { ApiErrorBody } from "@/types/api"

const DEFAULT_ERROR_MESSAGE =
  "An unexpected error occurred. Please try again."

export class ApiError extends Error {
  readonly status: number | null
  readonly code: string | null
  readonly details: ApiErrorBody | null
  readonly isNetworkError: boolean

  constructor({
    message,
    status = null,
    code = null,
    details = null,
    isNetworkError = false,
    cause,
  }: {
    message: string
    status?: number | null
    code?: string | null
    details?: ApiErrorBody | null
    isNetworkError?: boolean
    cause?: unknown
  }) {
    super(message, {
      cause,
    })

    this.name = "ApiError"
    this.status = status
    this.code = code
    this.details = details
    this.isNetworkError = isNetworkError
  }
}

function extractErrorMessage(
  body: ApiErrorBody | null,
  fallback: string
): string {
  if (body?.message) {
    return body.message
  }

  if (body?.detail) {
    return body.detail
  }

  if (body?.errors?.length) {
    return body.errors
      .map((error) => error.message)
      .join(", ")
  }

  return fallback || DEFAULT_ERROR_MESSAGE
}

export function normalizeApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error
  }

  if (!axios.isAxiosError<ApiErrorBody>(error)) {
    return new ApiError({
      message:
        error instanceof Error
          ? error.message
          : DEFAULT_ERROR_MESSAGE,
      cause: error,
    })
  }

  const responseBody = error.response?.data ?? null
  const status = error.response?.status ?? null

  const isNetworkError =
    !error.response &&
    Boolean(error.request)

  const fallbackMessage = isNetworkError
    ? "Unable to reach the server. Check your connection and try again."
    : error.message

  return new ApiError({
    message: extractErrorMessage(
      responseBody,
      fallbackMessage
    ),
    status,
    code:
      responseBody?.code ??
      error.code ??
      null,
    details: responseBody,
    isNetworkError,
    cause: error,
  })
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError
}