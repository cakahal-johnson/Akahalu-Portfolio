import "server-only"
import {
  serverEnv,
} from "@/config/server-env"

import {
  ApiError,
} from "@/lib/api/errors"

type ServerApiRequestOptions = {
  signal?: AbortSignal
  next?: NextFetchRequestConfig
}

export async function serverApiGet<
  TResponse,
>(
  endpoint: string,
  options:
    ServerApiRequestOptions = {}
): Promise<TResponse> {
  const url =
    new URL(
      endpoint.replace(
        /^\/+/,
        ""
      ),
      `${serverEnv.apiUrl}/`
    )

  const response =
    await fetch(
      url,
      {
        method:
          "GET",

        headers: {
          Accept:
            "application/json",
        },

        signal:
          options.signal,

        next:
          options.next ?? {
            revalidate:
              60,
          },
      }
    )

  if (
    !response.ok
  ) {
    let body:
      unknown =
      null

    try {
      body =
        await response.json()
    } catch {
      body =
        null
    }

    let message =
      response.statusText

    let code:
      string |
      null =
      null

    if (
      typeof body ===
        "object" &&
      body !==
        null &&
      "detail" in body
    ) {
      const detail =
        (
          body as {
            detail?:
              unknown
          }
        ).detail

      if (
        typeof detail ===
          "object" &&
        detail !==
          null
      ) {
        if (
          "message" in
            detail &&
          typeof detail.message ===
            "string"
        ) {
          message =
            detail.message
        }

        if (
          "code" in
            detail &&
          typeof detail.code ===
            "string"
        ) {
          code =
            detail.code
        }
      } else if (
        typeof detail ===
        "string"
      ) {
        message =
          detail
      }
    }

    throw new ApiError({
      message:
        message ||
        "The API request failed.",

      status:
        response.status,

      code,
    })
  }

  return (
    response.json()
  ) as Promise<TResponse>
}