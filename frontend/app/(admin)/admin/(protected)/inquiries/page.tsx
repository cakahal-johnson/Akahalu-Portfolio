import type { Metadata } from "next"

import { AdminInquiryManager } from "@/components/admin/inquiries/admin-inquiry-manager"

export const metadata: Metadata = {
  title: "Manage Inquiries",
  description: "Review and manage portfolio contact inquiries.",
}

export default function AdminInquiriesPage() {
  return <AdminInquiryManager />
}