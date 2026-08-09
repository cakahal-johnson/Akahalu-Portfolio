"use client"

import {
  AlertCircle,
  ArrowLeft,
  Loader2,
} from "lucide-react"
import Link from "next/link"
import {
  useEffect,
  useState,
} from "react"

import {
  AdminProjectEditor,
} from "@/components/admin/projects/admin-project-editor"

import {
  AdminProjectLifecycle,
} from "@/components/admin/projects/admin-project-lifecycle"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminProjectService,
} from "@/services/admin"

import type {
  ProjectAdminRead,
} from "@/types/portfolio/project"

type AdminProjectDetailManagerProps = {
  projectId: string
}

export function AdminProjectDetailManager({
  projectId,
}: AdminProjectDetailManagerProps) {
  const [
    project,
    setProject,
  ] =
    useState<ProjectAdminRead | null>(
      null
    )

  const [
    loading,
    setLoading,
  ] =
    useState(true)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  useEffect(() => {
    let cancelled =
      false

    const request =
      adminProjectService.getProject(
        projectId,
        {
          includeDeleted:
            true,
        }
      )

    void request
      .then(
        (result) => {
          if (
            cancelled
          ) {
            return
          }

          setProject(
            result
          )

          setError(
            null
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setError(
            caughtError instanceof
            AdminApiError
              ? caughtError.message
              : "The project could not be loaded."
          )
        }
      )
      .finally(
        () => {
          if (
            cancelled
          ) {
            return
          }

          setLoading(
            false
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    projectId,
  ])

  return (
    <div className="space-y-8">
      <div>
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
          {project
            ? project.title
            : "Manage project"}
        </h1>

        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          Edit project content and manage
          its publication, visibility and
          featured state.
        </p>
      </div>

      {error ? (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
        >
          <AlertCircle
            className="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />

          {error}
        </div>
      ) : null}

      {loading ? (
        <div className="flex min-h-72 items-center justify-center rounded-2xl border border-border bg-background">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2
              className="size-5 animate-spin"
              aria-hidden="true"
            />

            Loading project...
          </div>
        </div>
      ) : project ? (
        <>
          <AdminProjectLifecycle
            project={
              project
            }
            onProjectChange={
              setProject
            }
          />

          <AdminProjectEditor
            project={
              project
            }
            onProjectChange={
              setProject
            }
          />
        </>
      ) : !error ? (
        <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
          <h2 className="font-semibold">
            Project unavailable
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            The requested project could
            not be found.
          </p>
        </div>
      ) : null}
    </div>
  )
}