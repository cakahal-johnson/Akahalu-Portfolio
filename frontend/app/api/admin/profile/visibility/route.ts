import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

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
    "/admin/portfolio/profile/visibility",
    {
      method: "PATCH",
      body,
    }
  )
}