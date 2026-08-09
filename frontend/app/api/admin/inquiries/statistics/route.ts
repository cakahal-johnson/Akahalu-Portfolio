import {
  NextRequest,
} from "next/server"

import {
  proxyAuthenticatedAdminRequest,
} from "@/lib/auth/admin-proxy"

export async function GET(
  request: NextRequest
) {
  return proxyAuthenticatedAdminRequest(
    request,
    "/admin/contact/inquiries/statistics"
  )
}