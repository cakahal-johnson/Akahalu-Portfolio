import type {
  Metadata,
} from "next"

import {
  AdminTechnologyManager,
} from "@/components/admin/technologies/admin-technology-manager"

export const metadata:
  Metadata = {
    title:
      "Manage Technologies",

    description:
      "Manage portfolio technologies, tools, frameworks and services.",
  }

export default function AdminTechnologiesPage() {
  return (
    <AdminTechnologyManager />
  )
}