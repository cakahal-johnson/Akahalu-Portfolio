import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

const ADMIN_PROJECTS_PATH =
  "/admin/portfolio/projects"

export async function GET(
  request: NextRequest
) {
  const query =
    request.nextUrl.searchParams.toString()

  const backendPath =
    query
      ? `${ADMIN_PROJECTS_PATH}?${query}`
      : ADMIN_PROJECTS_PATH

  return proxyAuthenticatedAdminRequest(
    request,
    backendPath
  )
}