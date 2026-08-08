import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  ADMIN_ACCESS_TOKEN_COOKIE,
  ADMIN_REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants"

import {
  clearAuthenticationCookies,
  getBackendUser,
  isAdministrativeUser,
  refreshBackendSession,
  setAuthenticationCookies,
} from "@/lib/auth/server"

export async function GET(
  request: NextRequest
) {
  const accessToken =
    request.cookies.get(
      ADMIN_ACCESS_TOKEN_COOKIE
    )?.value

  const refreshToken =
    request.cookies.get(
      ADMIN_REFRESH_TOKEN_COOKIE
    )?.value

  if (accessToken) {
    try {
      const user =
        await getBackendUser(
          accessToken
        )

      if (
        user &&
        isAdministrativeUser(user)
      ) {
        return NextResponse.json(
          {
            user,
          }
        )
      }
    } catch {
      // Try refresh below.
    }
  }

  if (!refreshToken) {
    const response =
      NextResponse.json(
        {
          detail: {
            code:
              "authentication_required",
            message:
              "Administrator authentication is required.",
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
              "authentication_expired",
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
    NextResponse.json(
      {
        user:
          refreshed.user,
      }
    )

  setAuthenticationCookies(
    response,
    refreshed.tokens
  )

  return response
}