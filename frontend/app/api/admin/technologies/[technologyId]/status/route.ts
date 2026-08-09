import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    technologyId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The technology status request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const {
    technologyId,
  } =
    await context.params

  let body: unknown

  try {
    body =
      await request.json()
  } catch {
    return invalidJsonResponse()
  }

  return proxyAuthenticatedAdminRequest(
    request,
    `/admin/portfolio/technologies/${encodeURIComponent(
      technologyId
    )}/status`,
    {
      method:
        "PATCH",

      body,
    }
  )
}