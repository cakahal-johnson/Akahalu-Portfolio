import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    projectId: string
  }>
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const {
    projectId,
  } = await context.params

  let body: unknown

  try {
    body =
      await request.json()
  } catch {
    body = {}
  }

  return proxyAuthenticatedAdminRequest(
    request,
    `/admin/portfolio/projects/${encodeURIComponent(
      projectId
    )}/featured`,
    {
      method: "PATCH",
      body,
    }
  )
}