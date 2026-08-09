import type {
  Metadata,
} from "next"

import {
  AdminProjectDetailManager,
} from "@/components/admin/projects/admin-project-detail-manager"

export const metadata: Metadata = {
  title:
    "Manage Project",

  robots: {
    index:
      false,

    follow:
      false,
  },
}

type AdminProjectPageProps = {
  params: Promise<{
    projectId: string
  }>
}

export default async function AdminProjectPage({
  params,
}: AdminProjectPageProps) {
  const {
    projectId,
  } =
    await params

  return (
    <div className="mx-auto w-full max-w-7xl">
      <AdminProjectDetailManager
        projectId={
          projectId
        }
      />
    </div>
  )
}