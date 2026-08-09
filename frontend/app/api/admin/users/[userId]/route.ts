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
          "The user request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendUserPath(
  userId: string
): string {
  return `/admin/users/${encodeURIComponent(
    userId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    userId,
  } =
    await context.params

  const query =
    request.nextUrl.searchParams.toString()

  const userPath =
    backendUserPath(
      userId
    )

  const backendPath =
    query
      ? `${userPath}?${query}`
      : userPath

  return proxyAuthenticatedAdminRequest(
    request,
    backendPath
  )
}

export async function DELETE(
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
    backendUserPath(
      userId
    ),
    {
      method:
        "DELETE",

      body,
    }
  )
}