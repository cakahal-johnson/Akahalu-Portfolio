import { z } from "zod"

const publicEnvironmentSchema = z.object({
  NEXT_PUBLIC_APP_URL: z
    .url("NEXT_PUBLIC_APP_URL must be a valid URL")
    .default("http://localhost:3000"),

  NEXT_PUBLIC_API_URL: z
    .url("NEXT_PUBLIC_API_URL must be a valid URL")
    .default("http://127.0.0.1:8000/api/v1"),

  NEXT_PUBLIC_API_TIMEOUT_MS: z.coerce
    .number()
    .int()
    .positive()
    .max(120_000)
    .default(15_000),
})

const environmentResult = publicEnvironmentSchema.safeParse({
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_API_TIMEOUT_MS:
    process.env.NEXT_PUBLIC_API_TIMEOUT_MS,
})

if (!environmentResult.success) {
  const messages = environmentResult.error.issues
    .map((issue) => {
      const path = issue.path.join(".") || "environment"
      return `${path}: ${issue.message}`
    })
    .join("; ")

  throw new Error(`Invalid frontend environment: ${messages}`)
}

export const env = {
  appUrl: environmentResult.data.NEXT_PUBLIC_APP_URL,
  apiUrl: environmentResult.data.NEXT_PUBLIC_API_URL.replace(
    /\/+$/,
    ""
  ),
  apiTimeoutMs:
    environmentResult.data.NEXT_PUBLIC_API_TIMEOUT_MS,
} as const