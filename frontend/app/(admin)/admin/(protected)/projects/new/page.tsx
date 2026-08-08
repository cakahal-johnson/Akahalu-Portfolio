import type {
  Metadata,
} from "next"

import Link from "next/link"

import {
  ArrowLeft,
} from "lucide-react"

import { AdminProjectCreateForm } from "@/components/admin/projects/admin-project-create-form"
import { Button } from "@/components/ui/button"

export const metadata: Metadata = {
  title:
    "New Project",

  robots: {
    index:
      false,

    follow:
      false,
  },
}

export default function AdminNewProjectPage() {
  return (
    <div className="mx-auto w-full max-w-7xl">
      <div className="mb-8">
        <Button
          asChild
          variant="ghost"
          className="-ml-3 mb-4"
        >
          <Link href="/admin/projects">
            <ArrowLeft
              aria-hidden="true"
            />

            Back to projects
          </Link>
        </Button>

        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Portfolio projects
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Create project
        </h1>

        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          Create the project foundation,
          assign its category and
          technologies, and prepare its
          portfolio content. New projects
          remain private drafts until
          explicitly published.
        </p>
      </div>

      <AdminProjectCreateForm />
    </div>
  )
}