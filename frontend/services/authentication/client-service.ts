import type {
  AdminLoginRequest,
  AdminSessionResponse,
  AuthenticationErrorBody,
} from "@/types/authentication"

export class AdminAuthenticationError extends Error {
  readonly status: number
  readonly code: string | null

  constructor(
    message: string,
    {
      status,
      code = null,
    }: {
      status: number
      code?: string | null
    }
  ) {
    super(
      message
    )

    this.name =
      "AdminAuthenticationError"

    this.status =
      status

    this.code =
      code
  }
}

async function parseError(
  response: Response
): Promise<AdminAuthenticationError> {
  let body:
    | AuthenticationErrorBody
    | null = null

  try {
    body =
      (await response.json()) as AuthenticationErrorBody
  } catch {
    body =
      null
  }

  return new AdminAuthenticationError(
    body?.detail?.message ??
      body?.message ??
      "Authentication could not be completed.",
    {
      status:
        response.status,

      code:
        body?.detail?.code ??
        null,
    }
  )
}

async function requestSession(
  input: RequestInfo | URL,
  init?: RequestInit
): Promise<AdminSessionResponse> {
  let response:
    Response

  try {
    response =
      await fetch(
        input,
        {
          ...init,

          credentials:
            "same-origin",

          headers: {
            Accept:
              "application/json",

            ...(init?.headers ??
              {}),
          },

          cache:
            "no-store",
        }
      )
  } catch {
    throw new AdminAuthenticationError(
      "The authentication service could not be reached.",
      {
        status:
          0,

        code:
          "network_error",
      }
    )
  }

  if (
    !response.ok
  ) {
    throw await parseError(
      response
    )
  }

  return (
    await response.json()
  ) as AdminSessionResponse
}

export const adminAuthenticationService =
  {
    login(
      payload:
        AdminLoginRequest
    ): Promise<AdminSessionResponse> {
      return requestSession(
        "/api/admin-auth/login",
        {
          method:
            "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },

    getSession(): Promise<AdminSessionResponse> {
      return requestSession(
        "/api/admin-auth/session",
        {
          method:
            "GET",
        }
      )
    },

    refresh(): Promise<AdminSessionResponse> {
      return requestSession(
        "/api/admin-auth/refresh",
        {
          method:
            "POST",
        }
      )
    },

    async logout(): Promise<void> {
      let response:
        Response

      try {
        response =
          await fetch(
            "/api/admin-auth/logout",
            {
              method:
                "POST",

              credentials:
                "same-origin",

              cache:
                "no-store",
            }
          )
      } catch {
        throw new AdminAuthenticationError(
          "The authentication service could not be reached.",
          {
            status:
              0,

            code:
              "network_error",
          }
        )
      }

      if (
        !response.ok
      ) {
        throw await parseError(
          response
        )
      }
    },
  } as const