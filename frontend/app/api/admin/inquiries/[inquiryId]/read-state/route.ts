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
          "The inquiry read-state request body must contain valid JSON.",
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
    `/admin/contact/inquiries/${encodeURIComponent(
      inquiryId
    )}/read-state`,
    {
      method:
        "PATCH",

      body,
    }
  )
}