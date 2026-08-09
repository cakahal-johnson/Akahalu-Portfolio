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
          "The technology request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendTechnologyPath(
  technologyId: string
): string {
  return `/admin/portfolio/technologies/${encodeURIComponent(
    technologyId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    technologyId,
  } =
    await context.params

  const query =
    request.nextUrl.searchParams.toString()

  const technologyPath =
    backendTechnologyPath(
      technologyId
    )

  const backendPath =
    query
      ? `${technologyPath}?${query}`
      : technologyPath

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
    backendTechnologyPath(
      technologyId
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
    backendTechnologyPath(
      technologyId
    ),
    {
      method:
        "DELETE",

      body,
    }
  )
}