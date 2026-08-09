import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    projectId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The project request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendProjectPath(
  projectId: string
): string {
  return `/admin/portfolio/projects/${encodeURIComponent(
    projectId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    projectId,
  } =
    await context.params

  const query =
    request.nextUrl.searchParams.toString()

  const projectPath =
    backendProjectPath(
      projectId
    )

  const backendPath =
    query
      ? `${projectPath}?${query}`
      : projectPath

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
    projectId,
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
    backendProjectPath(
      projectId
    ),
    {
      method:
        "PATCH",

      body,
    }
  )
}