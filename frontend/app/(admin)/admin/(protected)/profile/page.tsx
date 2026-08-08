import type {
  Metadata,
} from "next"

import { AdminProfileEditor } from "@/components/admin/profile/admin-profile-editor"

export const metadata: Metadata = {
  title:
    "Manage Profile",
  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminProfilePage() {
  return (
    <div className="mx-auto w-full max-w-7xl">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Portfolio profile
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Manage profile
        </h1>

        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          Maintain the personal,
          professional, contact,
          availability, and search
          information displayed throughout
          the public portfolio.
        </p>
      </div>

      <AdminProfileEditor />
    </div>
  )
}