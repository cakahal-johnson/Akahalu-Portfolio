import "server-only"

import { NextResponse } from "next/server"

import { env } from "@/config/env"
import {
  ADMIN_ACCESS_TOKEN_COOKIE,
  ADMIN_REFRESH_TOKEN_COOKIE,
} from "@/lib/auth/constants"

import type {
  AuthenticatedUser,
  AuthenticationErrorBody,
  BackendRefreshResponse,
  TokenPair,
} from "@/types/authentication"

type BackendError = {
  status: number
  code: string | null
  message: string
}

function buildBackendUrl(
  path: string
): string {
  return `${env.apiUrl}${path}`
}

export async function parseBackendError(
  response: Response
): Promise<BackendError> {
  let payload:
    | AuthenticationErrorBody
    | null = null

  try {
    payload =
      (await response.json()) as AuthenticationErrorBody
  } catch {
    payload = null
  }

  return {
    status: response.status,
    code:
      payload?.detail?.code ??
      null,
    message:
      payload?.detail?.message ??
      payload?.message ??
      "Authentication could not be completed.",
  }
}

export function isAdministrativeUser(
  user: AuthenticatedUser
): boolean {
  if (
    !user.is_active ||
    !user.is_verified ||
    user.deleted_at !== null
  ) {
    return false
  }

  if (user.is_superuser) {
    return true
  }

  return user.roles.some(
    (role) =>
      role.is_active &&
      role.deleted_at === null
  )
}

export function setAuthenticationCookies(
  response: NextResponse,
  tokens: TokenPair
): void {
  const secure =
    process.env.NODE_ENV ===
    "production"

  response.cookies.set(
    ADMIN_ACCESS_TOKEN_COOKIE,
    tokens.access_token,
    {
      httpOnly: true,
      secure,
      sameSite: "lax",
      path: "/",
      expires: new Date(
        tokens.access_token_expires_at
      ),
    }
  )

  response.cookies.set(
    ADMIN_REFRESH_TOKEN_COOKIE,
    tokens.refresh_token,
    {
      httpOnly: true,
      secure,
      sameSite: "lax",
      path: "/",
      expires: new Date(
        tokens.refresh_token_expires_at
      ),
    }
  )
}

export function clearAuthenticationCookies(
  response: NextResponse
): void {
  response.cookies.set(
    ADMIN_ACCESS_TOKEN_COOKIE,
    "",
    {
      httpOnly: true,
      secure:
        process.env.NODE_ENV ===
        "production",
      sameSite: "lax",
      path: "/",
      expires: new Date(0),
    }
  )

  response.cookies.set(
    ADMIN_REFRESH_TOKEN_COOKIE,
    "",
    {
      httpOnly: true,
      secure:
        process.env.NODE_ENV ===
        "production",
      sameSite: "lax",
      path: "/",
      expires: new Date(0),
    }
  )
}

export async function getBackendUser(
  accessToken: string
): Promise<
  AuthenticatedUser | null
> {
  const response = await fetch(
    buildBackendUrl("/auth/me"),
    {
      method: "GET",
      headers: {
        Accept:
          "application/json",
        Authorization:
          `Bearer ${accessToken}`,
      },
      cache: "no-store",
    }
  )

  if (!response.ok) {
    return null
  }

  return (await response.json()) as AuthenticatedUser
}

export async function refreshBackendSession(
  refreshToken: string
): Promise<
  BackendRefreshResponse | null
> {
  const response = await fetch(
    buildBackendUrl(
      "/auth/refresh"
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

  if (!response.ok) {
    return null
  }

  return (await response.json()) as BackendRefreshResponse
}

export { buildBackendUrl }