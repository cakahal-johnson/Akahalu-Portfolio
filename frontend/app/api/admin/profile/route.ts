import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

const PROFILE_PATH =
  "/admin/portfolio/profile"

export async function GET(
  request: NextRequest
) {
  return proxyAuthenticatedAdminRequest(
    request,
    PROFILE_PATH
  )
}

export async function PATCH(
  request: NextRequest
) {
  let body: unknown

  try {
    body =
      await request.json()
  } catch {
    body = {}
  }

  return proxyAuthenticatedAdminRequest(
    request,
    PROFILE_PATH,
    {
      method: "PATCH",
      body,
    }
  )
}