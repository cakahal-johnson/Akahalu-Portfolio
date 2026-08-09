import type {
  Metadata,
} from "next"

import {
  AdminExperienceManager,
} from "@/components/admin/experiences/admin-experience-manager"

export const metadata:
  Metadata = {
    title:
      "Manage Experience",

    description:
      "Manage professional experience and public portfolio employment history.",
  }

export default function AdminExperiencePage() {
  return (
    <AdminExperienceManager />
  )
}