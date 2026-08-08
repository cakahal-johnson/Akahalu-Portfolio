import type {
  Metadata,
} from "next"

import { AdminProjectManager } from "@/components/admin/projects/admin-project-manager"

export const metadata: Metadata = {
  title:
    "Manage Projects",

  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminProjectsPage() {
  return (
    <div className="mx-auto w-full max-w-7xl">
      <AdminProjectManager />
    </div>
  )
}