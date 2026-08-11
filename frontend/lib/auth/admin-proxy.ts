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
        status:
          401,

        headers: {
          "Cache-Control":
            "no-store",
        },
      }
    )

  clearAuthenticationCookies(
    response
  )

  return response
}

function refreshRequiredResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "access_token_refresh_required",

        message:
          "The administrator access token must be refreshed.",
      },
    },
    {
      status:
        401,

      headers: {
        "Cache-Control":
          "no-store",
      },
    }
  )
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
      status:
        503,

      headers: {
        "Cache-Control":
          "no-store",
      },
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
    buildBackendUrl(
      path
    ),
    {
      method:
        options.method ??
        "GET",

      headers,

      body,

      cache:
        "no-store",
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

  /*
   * Refresh-token rotation is intentionally
   * NOT performed here.
   *
   * Several admin requests may run in parallel.
   * If each BFF handler independently attempted
   * to rotate the same refresh token, legitimate
   * concurrent requests could trigger backend
   * refresh-token reuse protection.
   *
   * Client-side adminRequest() serializes refresh
   * into one shared refresh operation and retries
   * the original requests afterwards.
   */

  if (!accessToken) {
    if (refreshToken) {
      return refreshRequiredResponse()
    }

    return authenticationRequiredResponse()
  }

  let backendResponse:
    Response

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

  if (!refreshToken) {
    return authenticationRequiredResponse(
      "Your administrator session is no longer valid. Please sign in again."
    )
  }

  return refreshRequiredResponse()
}