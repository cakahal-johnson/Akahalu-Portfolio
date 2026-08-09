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
          "The category request body must contain valid JSON.",
      },
    },
    {
      status: 400,
    }
  )
}

function backendCategoryPath(
  categoryId: string
): string {
  return `/admin/portfolio/categories/${encodeURIComponent(
    categoryId
  )}`
}

export async function GET(
  request: NextRequest,
  context: RouteContext
) {
  const {
    categoryId,
  } =
    await context.params

  const query =
    request.nextUrl.searchParams.toString()

  const categoryPath =
    backendCategoryPath(
      categoryId
    )

  const backendPath =
    query
      ? `${categoryPath}?${query}`
      : categoryPath

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
    backendCategoryPath(
      categoryId
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
    backendCategoryPath(
      categoryId
    ),
    {
      method:
        "DELETE",

      body,
    }
  )
}