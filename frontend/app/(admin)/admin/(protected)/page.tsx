import type {
  Metadata,
} from "next"

import {
  AdminDashboard,
} from "@/components/admin/dashboard/admin-dashboard"

export const metadata:
  Metadata = {
    title:
      "Administration",

    description:
      "Manage portfolio content, inquiries and administrative accounts.",

    robots: {
      index:
        false,

      follow:
        false,
    },
  }

export default function AdminDashboardPage() {
  return (
    <AdminDashboard />
  )
}