import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

const ADMIN_TECHNOLOGIES_PATH =
  "/admin/portfolio/technologies"

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

export async function GET(
  request: NextRequest
) {
  const query =
    request.nextUrl.searchParams.toString()

  const backendPath =
    query
      ? `${ADMIN_TECHNOLOGIES_PATH}?${query}`
      : ADMIN_TECHNOLOGIES_PATH

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
    ADMIN_TECHNOLOGIES_PATH,
    {
      method:
        "POST",

      body,
    }
  )
}