"use client"

import {
  AlertCircle,
  ExternalLink,
  Loader2,
  Star,
} from "lucide-react"
import Link from "next/link"
import {
  useState,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  cn,
} from "@/lib/utils"

import {
  AdminApiError,
  adminProjectService,
} from "@/services/admin"

import type {
  ProjectAdminRead,
} from "@/types/portfolio/project"

import type {
  ProjectVisibility,
} from "@/types/portfolio/common"

type AdminProjectLifecycleProps = {
  project:
    ProjectAdminRead

  onProjectChange: (
    project:
      ProjectAdminRead
  ) => void
}

type BusyAction =
  | "publish"
  | "draft"
  | "archive"
  | "visibility"
  | "featured"

function statusClass(
  status:
    ProjectAdminRead["status"]
): string {
  if (
    status ===
    "published"
  ) {
    return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
  }

  if (
    status ===
    "archived"
  ) {
    return "bg-muted text-muted-foreground"
  }

  return "bg-amber-500/10 text-amber-700 dark:text-amber-400"
}

export function AdminProjectLifecycle({
  project,
  onProjectChange,
}: AdminProjectLifecycleProps) {
  const [
    busyAction,
    setBusyAction,
  ] =
    useState<BusyAction | null>(
      null
    )

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  const deleted =
    project.deleted_at !== null

  const published =
    project.status ===
    "published"

  const canFeature =
    published &&
    project.visibility ===
      "public" &&
    !deleted

    const canViewPublic =
    published &&
    project.visibility ===
      "public" &&
    project.published_at !==
      null &&
    !deleted

  async function runAction(
    action:
      BusyAction,
    operation:
      () => Promise<ProjectAdminRead>
  ) {
    if (
      busyAction
    ) {
      return
    }

    try {
      setBusyAction(
        action
      )

      setError(
        null
      )

      const updated =
        await operation()

      onProjectChange(
        updated
      )
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The project lifecycle could not be updated."
      )
    } finally {
      setBusyAction(
        null
      )
    }
  }

  function publishProject() {
    if (
      !project.category_id
    ) {
      setError(
        "Assign a project category before publishing."
      )

      return
    }

    void runAction(
      "publish",
      () =>
        adminProjectService.updateStatus(
          project.id,
          {
            status:
              "published",

            published_at:
              new Date().toISOString(),

            reason:
              "Project published from portfolio administration.",
          }
        )
    )
  }

  function moveToDraft() {
    void runAction(
      "draft",
      () =>
        adminProjectService.updateStatus(
          project.id,
          {
            status:
              "draft",

            reason:
              "Project returned to draft from portfolio administration.",
          }
        )
    )
  }

  function archiveProject() {
    void runAction(
      "archive",
      () =>
        adminProjectService.updateStatus(
          project.id,
          {
            status:
              "archived",

            reason:
              "Project archived from portfolio administration.",
          }
        )
    )
  }

  function changeVisibility(
    visibility:
      ProjectVisibility
  ) {
    void runAction(
      "visibility",
      () =>
        adminProjectService.updateVisibility(
          project.id,
          {
            visibility,

            reason:
              "Project visibility updated from portfolio administration.",
          }
        )
    )
  }

  function toggleFeatured() {
    void runAction(
      "featured",
      () =>
        adminProjectService.updateFeatured(
          project.id,
          {
            is_featured:
              !project.is_featured,

            reason:
              "Featured state updated from portfolio administration.",
          }
        )
    )
  }

  return (
    <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <p className="text-sm font-semibold">
            Project lifecycle
          </p>

          <p className="mt-1 max-w-2xl text-sm leading-6 text-muted-foreground">
            Publication, visibility and
            featured state are managed
            separately from project
            content.
          </p>

          <div className="mt-4 flex flex-wrap gap-2">
            <span
              className={cn(
                "rounded-full px-2.5 py-1 text-xs font-medium capitalize",
                statusClass(
                  project.status
                )
              )}
            >
              {project.status}
            </span>

            <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium capitalize text-muted-foreground">
              {
                project.visibility
              }
            </span>

            {project.is_featured ? (
              <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                Featured
              </span>
            ) : null}

            {deleted ? (
              <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                Deleted
              </span>
            ) : null}
          </div>
        </div>

        {canViewPublic ? (
          <Button
            asChild
            variant="outline"
            size="sm"
          >
            <Link
              href={`/projects/${encodeURIComponent(
                project.slug
              )}`}
              target="_blank"
            >
              <ExternalLink
                aria-hidden="true"
              />

              View public project
            </Link>
          </Button>
        ) : null}
      </div>

      {error ? (
        <div
          role="alert"
          className="mt-5 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
        >
          <AlertCircle
            className="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />

          {error}
        </div>
      ) : null}

      {deleted ? (
        <div className="mt-5 rounded-xl border border-border bg-muted/30 p-4 text-sm text-muted-foreground">
          Lifecycle controls are disabled
          while this project is deleted.
        </div>
      ) : (
        <div className="mt-6 grid gap-6 xl:grid-cols-3">
          <div className="rounded-xl border border-border p-4">
            <h3 className="font-medium">
              Publication
            </h3>

            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Published projects become
              publicly visible. Archiving
              hides the project and removes
              featured state.
            </p>

            <div className="mt-4 flex flex-wrap gap-2">
              {!published ? (
                <Button
                  type="button"
                  size="sm"
                  disabled={
                    busyAction !==
                    null
                  }
                  onClick={
                    publishProject
                  }
                >
                  {busyAction ===
                  "publish" ? (
                    <Loader2
                      className="animate-spin"
                      aria-hidden="true"
                    />
                  ) : null}

                  Publish
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    busyAction !==
                    null
                  }
                  onClick={
                    moveToDraft
                  }
                >
                  {busyAction ===
                  "draft" ? (
                    <Loader2
                      className="animate-spin"
                      aria-hidden="true"
                    />
                  ) : null}

                  Unpublish
                </Button>
              )}

              {project.status !==
              "archived" ? (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    busyAction !==
                    null
                  }
                  onClick={
                    archiveProject
                  }
                >
                  {busyAction ===
                  "archive" ? (
                    <Loader2
                      className="animate-spin"
                      aria-hidden="true"
                    />
                  ) : null}

                  Archive
                </Button>
              ) : (
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    busyAction !==
                    null
                  }
                  onClick={
                    moveToDraft
                  }
                >
                  {busyAction ===
                  "draft" ? (
                    <Loader2
                      className="animate-spin"
                      aria-hidden="true"
                    />
                  ) : null}

                  Move to draft
                </Button>
              )}
            </div>

            {!project.category_id ? (
              <p className="mt-3 text-xs text-amber-700 dark:text-amber-400">
                A category is required
                before publishing.
              </p>
            ) : null}
          </div>

          <div className="rounded-xl border border-border p-4">
            <h3 className="font-medium">
              Visibility
            </h3>

            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Public projects appear in the
              portfolio. Unlisted projects
              can remain published without
              appearing in normal public
              listings.
            </p>

            <div className="mt-4">
                            <select
                value={
                  published
                    ? project.visibility
                    : "public"
                }
                disabled={
                  !published ||
                  busyAction !==
                    null
                }
                onChange={(event) =>
                  changeVisibility(
                    event.target
                      .value as ProjectVisibility
                  )
                }
                className="h-10 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="public">
                  Public
                </option>

                <option value="unlisted">
                  Unlisted
                </option>
              </select>

              {busyAction ===
              "visibility" ? (
                <p className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <Loader2
                    className="size-3 animate-spin"
                    aria-hidden="true"
                  />

                  Updating visibility...
                </p>
              ) : null}

              {!published ? (
                <p className="mt-2 text-xs text-muted-foreground">
                  Publish the project before
                  changing its visibility.
                </p>
              ) : null}
            </div>
          </div>

          <div className="rounded-xl border border-border p-4">
            <h3 className="font-medium">
              Featured project
            </h3>

            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Only published public
              projects can be promoted as
              featured portfolio work.
            </p>

            <div className="mt-4">
              <Button
                type="button"
                variant={
                  project.is_featured
                    ? "secondary"
                    : "outline"
                }
                size="sm"
                disabled={
                  (!canFeature &&
                    !project.is_featured) ||
                  busyAction !==
                    null
                }
                onClick={
                  toggleFeatured
                }
              >
                {busyAction ===
                "featured" ? (
                  <Loader2
                    className="animate-spin"
                    aria-hidden="true"
                  />
                ) : (
                  <Star
                    aria-hidden="true"
                  />
                )}

                {project.is_featured
                  ? "Unfeature"
                  : "Feature project"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}