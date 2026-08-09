import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    userId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The user restore request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendUserRestorePath(
  userId: string
): string {
  return `/admin/users/${encodeURIComponent(
    userId
  )}/restore`
}

export async function POST(
  request: NextRequest,
  context: RouteContext
) {
  const {
    userId,
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
    backendUserRestorePath(
      userId
    ),
    {
      method:
        "POST",

      body,
    }
  )
}