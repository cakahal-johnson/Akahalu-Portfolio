import {
  ADMIN_LOGIN_PATH,
} from "@/lib/auth/constants"

import {
  adminAuthenticationService,
} from "@/services/authentication"

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
    super(
      message
    )

    this.name =
      "AdminApiError"

    this.status =
      status

    this.code =
      code
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
    payload =
      null
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

async function performAdminRequest(
  url: string,
  init?: RequestInit
): Promise<Response> {
  const headers =
    new Headers(
      init?.headers
    )

  if (
    !headers.has(
      "Accept"
    )
  ) {
    headers.set(
      "Accept",
      "application/json"
    )
  }

  if (
    init?.body &&
    !headers.has(
      "Content-Type"
    )
  ) {
    headers.set(
      "Content-Type",
      "application/json"
    )
  }

  try {
    return await fetch(
      url,
      {
        ...init,

        credentials:
          "same-origin",

        headers,

        cache:
          "no-store",
      }
    )
  } catch {
    throw new AdminApiError(
      "The administration service could not be reached.",
      {
        status:
          0,

        code:
          "network_error",
      }
    )
  }
}

let refreshPromise:
  Promise<void> |
  null =
  null

function refreshAdminSessionOnce(): Promise<void> {
  if (
    refreshPromise
  ) {
    return refreshPromise
  }

  refreshPromise =
    adminAuthenticationService
      .refresh()
      .then(
        () =>
          undefined
      )
      .finally(
        () => {
          refreshPromise =
            null
        }
      )

  return refreshPromise
}

function redirectToLogin(): void {
  if (
    typeof window ===
    "undefined"
  ) {
    return
  }

  window.location.assign(
    ADMIN_LOGIN_PATH
  )
}

export async function adminRequest<
  TResponse,
>(
  url: string,
  init?: RequestInit
): Promise<TResponse> {
  let response =
    await performAdminRequest(
      url,
      init
    )

  if (
    response.status ===
    401
  ) {
    try {
      /*
       * All concurrent admin requests in this
       * browser runtime share the same promise.
       * Only one refresh request is therefore
       * sent while the others wait.
       */
      await refreshAdminSessionOnce()
    } catch {
      redirectToLogin()

      throw new AdminApiError(
        "Your administrator session has expired. Please sign in again.",
        {
          status:
            401,

          code:
            "authentication_required",
        }
      )
    }

    response =
      await performAdminRequest(
        url,
        init
      )
  }

  if (
    !response.ok
  ) {
    const error =
      await parseAdminError(
        response
      )

    if (
      error.status ===
      401
    ) {
      redirectToLogin()
    }

    throw error
  }

  if (
    response.status ===
    204
  ) {
    return undefined as TResponse
  }

  return (
    await response.json()
  ) as TResponse
}