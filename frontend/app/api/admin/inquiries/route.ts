import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

export async function GET(
  request: NextRequest
) {
  const query =
    request.nextUrl.search

  return proxyAuthenticatedAdminRequest(
    request,
    `/admin/contact/inquiries${query}`
  )
}