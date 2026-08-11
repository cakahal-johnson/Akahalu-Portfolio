import "server-only"

import {
  z,
} from "zod"

const defaultBackendApiUrl =
  "http://127.0.0.1:8000/api/v1"

const serverEnvironmentSchema =
  z.object({
    BACKEND_API_URL:
      z
        .url(
          "BACKEND_API_URL must be a valid URL"
        )
        .default(
          defaultBackendApiUrl
        ),
  })

const environmentResult =
  serverEnvironmentSchema.safeParse({
    BACKEND_API_URL:
      process.env.BACKEND_API_URL ??
      process.env.NEXT_PUBLIC_API_URL,
  })

if (
  !environmentResult.success
) {
  const messages =
    environmentResult.error.issues
      .map(
        (
          issue
        ) => {
          const path =
            issue.path.join(
              "."
            ) ||
            "environment"

          return `${path}: ${issue.message}`
        }
      )
      .join(
        "; "
      )

  throw new Error(
    `Invalid server environment: ${messages}`
  )
}

export const serverEnv = {
  apiUrl:
    environmentResult.data
      .BACKEND_API_URL
      .replace(
        /\/+$/,
        ""
      ),
} as const