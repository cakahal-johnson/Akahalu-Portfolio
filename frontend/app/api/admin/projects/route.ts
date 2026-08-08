import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

const ADMIN_PROJECTS_PATH =
  "/admin/portfolio/projects"

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

export async function POST(
  request: NextRequest
) {
  let body: unknown

  try {
    body =
      await request.json()
  } catch {
    return invalidJsonResponse()
  }

  return proxyAuthenticatedAdminRequest(
    request,
    ADMIN_PROJECTS_PATH,
    {
      method:
        "POST",

      body,
    }
  )
}