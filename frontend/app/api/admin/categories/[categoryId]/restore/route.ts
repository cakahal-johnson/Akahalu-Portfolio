import {
  NextRequest,
  NextResponse,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

type RouteContext = {
  params: Promise<{
    categoryId: string
  }>
}

function invalidJsonResponse(): NextResponse {
  return NextResponse.json(
    {
      detail: {
        code:
          "invalid_request_body",

        message:
          "The category restore request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

export async function POST(
  request: NextRequest,
  context: RouteContext
) {
  const {
    categoryId,
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
    `/admin/portfolio/categories/${encodeURIComponent(
      categoryId
    )}/restore`,
    {
      method:
        "POST",

      body,
    }
  )
}