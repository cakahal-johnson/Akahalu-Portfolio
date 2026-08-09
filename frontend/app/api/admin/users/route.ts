import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

const ADMIN_USERS_PATH =
  "/admin/users"

export async function GET(
  request: NextRequest
) {
  const query =
    request.nextUrl.searchParams.toString()

  const backendPath =
    query
      ? `${ADMIN_USERS_PATH}?${query}`
      : ADMIN_USERS_PATH

  return proxyAuthenticatedAdminRequest(
    request,
    backendPath
  )
}