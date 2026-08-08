import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  buildBackendUrl,
  isAdministrativeUser,
  parseBackendError,
  setAuthenticationCookies,
} from "@/lib/auth/server"

import type {
  AdminLoginRequest,
  BackendLoginRequest,
  BackendLoginResponse,
} from "@/types/authentication"

export async function POST(
  request: NextRequest
) {
  let payload: AdminLoginRequest

  try {
    payload =
      (await request.json()) as AdminLoginRequest
  } catch {
    return NextResponse.json(
      {
        detail: {
          code: "invalid_request",
          message:
            "A valid login request is required.",
        },
      },
      {
        status: 400,
      }
    )
  }

  const email =
    payload.email
      ?.trim()
      .toLowerCase()

  const password =
    payload.password

  if (!email || !password) {
    return NextResponse.json(
      {
        detail: {
          code: "invalid_request",
          message:
            "Email and password are required.",
        },
      },
      {
        status: 422,
      }
    )
  }

  const backendPayload: BackendLoginRequest =
    {
      email,
      password,
      device_name:
        "Akahalu Portfolio Admin",
    }

  let backendResponse: Response

  try {
    backendResponse =
      await fetch(
        buildBackendUrl(
          "/auth/login"
        ),
        {
          method: "POST",
          headers: {
            Accept:
              "application/json",
            "Content-Type":
              "application/json",

            "User-Agent":
              request.headers.get(
                "user-agent"
              ) ??
              "Akahalu-Portfolio-Admin",
          },
          body: JSON.stringify(
            backendPayload
          ),
          cache: "no-store",
        }
      )
  } catch {
    return NextResponse.json(
      {
        detail: {
          code: "backend_unavailable",
          message:
            "The authentication service is currently unavailable.",
        },
      },
      {
        status: 503,
      }
    )
  }

  if (!backendResponse.ok) {
    const error =
      await parseBackendError(
        backendResponse
      )

    return NextResponse.json(
      {
        detail: {
          code:
            error.code ??
            "authentication_failed",
          message:
            error.message,
        },
      },
      {
        status: error.status,
      }
    )
  }

  const login =
    (await backendResponse.json()) as BackendLoginResponse

  if (
    !isAdministrativeUser(
      login.user
    )
  ) {
    /*
     * The credentials may be valid,
     * but this application endpoint
     * is specifically for administration.
     *
     * Revoke the newly-created FastAPI
     * session before returning.
     */
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
              login.tokens
                .refresh_token,
          }),
          cache: "no-store",
        }
      )
    } catch {
      // Best-effort cleanup.
    }

    return NextResponse.json(
      {
        detail: {
          code:
            "admin_access_required",
          message:
            "This account does not have administrative access.",
        },
      },
      {
        status: 403,
      }
    )
  }

  const response =
    NextResponse.json(
      {
        user: login.user,
      },
      {
        status: 200,
      }
    )

  setAuthenticationCookies(
    response,
    login.tokens
  )

  return response
}