import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  ADMIN_REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants"

import {
  buildBackendUrl,
  clearAuthenticationCookies,
} from "@/lib/auth/server"

export async function POST(
  request: NextRequest
) {
  const refreshToken =
    request.cookies.get(
      ADMIN_REFRESH_TOKEN_COOKIE
    )?.value

  if (refreshToken) {
    try {
      await fetch(
        buildBackendUrl(
          "/auth/logout"
        ),
        {
          method: "POST",
          headers: {
            Accept:
              "application/json",
            "Content-Type":
              "application/json",
          },
          body: JSON.stringify({
            refresh_token:
              refreshToken,
          }),
          cache: "no-store",
        }
      )
    } catch {
      /*
       * Local cookies still need to
       * be cleared even if FastAPI is
       * temporarily unavailable.
       */
    }
  }

  const response =
    new NextResponse(
      null,
      {
        status: 204,
      }
    )

  clearAuthenticationCookies(
    response
  )

  return response
}