import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  ADMIN_REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants"

import {
  clearAuthenticationCookies,
  isAdministrativeUser,
  refreshBackendSession,
  setAuthenticationCookies,
} from "@/lib/auth/server"

export async function POST(
  request: NextRequest
) {
  const refreshToken =
    request.cookies.get(
      ADMIN_REFRESH_TOKEN_COOKIE
    )?.value

  if (!refreshToken) {
    const response =
      NextResponse.json(
        {
          detail: {
            code:
              "refresh_token_missing",
            message:
              "The administrator session cannot be refreshed.",
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

  let refreshed

  try {
    refreshed =
      await refreshBackendSession(
        refreshToken
      )
  } catch {
    refreshed = null
  }

  if (
    !refreshed ||
    !isAdministrativeUser(
      refreshed.user
    )
  ) {
    const response =
      NextResponse.json(
        {
          detail: {
            code:
              "refresh_failed",
            message:
              "Your administrator session has expired. Please sign in again.",
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

  const response =
    NextResponse.json({
      user: refreshed.user,
    })

  setAuthenticationCookies(
    response,
    refreshed.tokens
  )

  return response
}