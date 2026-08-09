import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    experienceId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The experience request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendExperiencePath(
  experienceId: string
): string {
  return `/admin/portfolio/experiences/${encodeURIComponent(
    experienceId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    experienceId,
  } =
    await context.params

  const query =
    request.nextUrl.searchParams.toString()

  const experiencePath =
    backendExperiencePath(
      experienceId
    )

  const backendPath =
    query
      ? `${experiencePath}?${query}`
      : experiencePath

  return proxyAuthenticatedAdminRequest(
    request,
    backendPath
  )
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const {
    experienceId,
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
    backendExperiencePath(
      experienceId
    ),
    {
      method:
        "PATCH",

      body,
    }
  )
}

export async function DELETE(
  request: NextRequest,
  context: RouteContext
) {
  const {
    experienceId,
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
    backendExperiencePath(
      experienceId
    ),
    {
      method:
        "DELETE",

      body,
    }
  )
}