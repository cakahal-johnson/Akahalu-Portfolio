import type {
  Metadata,
} from "next"

import {
  AdminCategoryManager,
} from "@/components/admin/categories/admin-category-manager"

export const metadata: Metadata = {
  title:
    "Manage Categories",

  robots: {
    index:
      false,

    follow:
      false,
  },
}

export default function AdminCategoriesPage() {
  return (
    <div className="mx-auto w-full max-w-7xl">
      <AdminCategoryManager />
    </div>
  )
}