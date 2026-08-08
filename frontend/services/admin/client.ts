type AdminErrorBody = {
  detail?:
    | string
    | {
        code?: string
        message?: string
      }

  message?: string
}

export class AdminApiError extends Error {
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
    super(message)

    this.name =
      "AdminApiError"

    this.status = status
    this.code = code
  }
}

async function parseAdminError(
  response: Response
): Promise<AdminApiError> {
  let payload:
    | AdminErrorBody
    | null = null

  try {
    payload =
      (await response.json()) as AdminErrorBody
  } catch {
    payload = null
  }

  const detail =
    payload?.detail

  const message =
    typeof detail ===
    "string"
      ? detail
      : detail?.message ??
        payload?.message ??
        "The administration request could not be completed."

  const code =
    typeof detail ===
    "object"
      ? detail?.code ??
        null
      : null

  return new AdminApiError(
    message,
    {
      status:
        response.status,
      code,
    }
  )
}

export async function adminRequest<
  TResponse,
>(
  url: string,
  init?: RequestInit
): Promise<TResponse> {
  let response: Response

  try {
    response =
      await fetch(
        url,
        {
          ...init,

          credentials:
            "same-origin",

          headers: {
            Accept:
              "application/json",

            ...(init?.body
              ? {
                  "Content-Type":
                    "application/json",
                }
              : {}),

            ...(init?.headers ??
              {}),
          },

          cache:
            "no-store",
        }
      )
  } catch {
    throw new AdminApiError(
      "The administration service could not be reached.",
      {
        status: 0,
        code:
          "network_error",
      }
    )
  }

  if (!response.ok) {
    throw await parseAdminError(
      response
    )
  }

  return (await response.json()) as TResponse
}