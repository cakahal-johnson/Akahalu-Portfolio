import type {
  Metadata,
} from "next"

import {
  AdminUserManager,
} from "@/components/admin/users/admin-user-manager"

export const metadata:
  Metadata = {
    title:
      "Manage Users",

    description:
      "Manage portfolio administrator and user account lifecycle.",
  }

export default function AdminUsersPage() {
  return (
    <AdminUserManager />
  )
}