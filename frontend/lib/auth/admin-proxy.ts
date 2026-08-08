import "server-only"

import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  ADMIN_ACCESS_TOKEN_COOKIE,
  ADMIN_REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants"

import {
  buildBackendUrl,
  clearAuthenticationCookies,
  isAdministrativeUser,
  refreshBackendSession,
  setAuthenticationCookies,
} from "@/lib/auth/server"

type AdminProxyOptions = {
  method?: string
  body?: unknown
}

function authenticationRequiredResponse(
  message =
    "Administrator authentication is required."
): NextResponse {
  const response =
    NextResponse.json(
      {
        detail: {
          code:
            "authentication_required",
          message,
        },
      },
      {
        status: 401,
      }
    )

  clearAuthenticationCookies(
    response
  )

  return response
}

function backendUnavailableResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "backend_unavailable",
        message:
          "The administration service is currently unavailable.",
      },
    },
    {
      status: 503,
    }
  )
}

async function forwardBackendResponse(
  backendResponse: Response
): Promise<NextResponse> {
  const body =
    await backendResponse.text()

  const contentType =
    backendResponse.headers.get(
      "content-type"
    )

  const response =
    new NextResponse(
      body || null,
      {
        status:
          backendResponse.status,
      }
    )

  if (contentType) {
    response.headers.set(
      "Content-Type",
      contentType
    )
  }

  response.headers.set(
    "Cache-Control",
    "no-store"
  )

  return response
}

async function callBackend(
  path: string,
  accessToken: string,
  options: AdminProxyOptions
): Promise<Response> {
  const headers =
    new Headers({
      Accept:
        "application/json",
      Authorization:
        `Bearer ${accessToken}`,
    })

  let body:
    | string
    | undefined

  if (
    options.body !==
    undefined
  ) {
    headers.set(
      "Content-Type",
      "application/json"
    )

    body =
      JSON.stringify(
        options.body
      )
  }

  return fetch(
    buildBackendUrl(path),
    {
      method:
        options.method ??
        "GET",
      headers,
      body,
      cache: "no-store",
    }
  )
}

export async function proxyAuthenticatedAdminRequest(
  request: NextRequest,
  path: string,
  options: AdminProxyOptions = {}
): Promise<NextResponse> {
  const accessToken =
    request.cookies.get(
      ADMIN_ACCESS_TOKEN_COOKIE
    )?.value

  const refreshToken =
    request.cookies.get(
      ADMIN_REFRESH_TOKEN_COOKIE
    )?.value

  let backendResponse:
    | Response
    | null = null

  if (accessToken) {
    try {
      backendResponse =
        await callBackend(
          path,
          accessToken,
          options
        )
    } catch {
      return backendUnavailableResponse()
    }

    if (
      backendResponse.status !==
      401
    ) {
      return forwardBackendResponse(
        backendResponse
      )
    }
  }

  if (!refreshToken) {
    return authenticationRequiredResponse()
  }

  let refreshed

  try {
    refreshed =
      await refreshBackendSession(
        refreshToken
      )
  } catch {
    return backendUnavailableResponse()
  }

  if (
    !refreshed ||
    !isAdministrativeUser(
      refreshed.user
    )
  ) {
    return authenticationRequiredResponse(
      "Your administrator session has expired. Please sign in again."
    )
  }

  try {
    backendResponse =
      await callBackend(
        path,
        refreshed.tokens
          .access_token,
        options
      )
  } catch {
    return backendUnavailableResponse()
  }

  if (
    backendResponse.status ===
    401
  ) {
    return authenticationRequiredResponse(
      "Your administrator session is no longer valid. Please sign in again."
    )
  }

  const response =
    await forwardBackendResponse(
      backendResponse
    )

  /*
   * Refresh tokens rotate on every
   * successful refresh, so always
   * replace both cookies.
   */
  setAuthenticationCookies(
    response,
    refreshed.tokens
  )

  return response
}