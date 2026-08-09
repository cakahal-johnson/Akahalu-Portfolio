import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    inquiryId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The inquiry request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function inquiryPath(
  inquiryId: string
): string {
  return `/admin/contact/inquiries/${encodeURIComponent(
    inquiryId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    inquiryId,
  } =
    await context.params

  const query =
    request.nextUrl.search

  return proxyAuthenticatedAdminRequest(
    request,
    `${inquiryPath(
      inquiryId
    )}${query}`
  )
}

export async function PATCH(
  request: NextRequest,
  context: RouteContext
) {
  const {
    inquiryId,
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
    inquiryPath(
      inquiryId
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
    inquiryId,
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
    inquiryPath(
      inquiryId
    ),
    {
      method:
        "DELETE",

      body,
    }
  )
}