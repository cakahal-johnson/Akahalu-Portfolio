"use client"

import {
  ExternalLink,
  Eye,
  EyeOff,
  Loader2,
  Star,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

import type {
  ProjectAdminRead,
} from "@/types/portfolio/project"

type AdminProjectCardProps = {
  project: ProjectAdminRead

  busyAction:
    | "visibility"
    | "featured"
    | null

  onToggleVisibility: (
    project: ProjectAdminRead
  ) => void

  onToggleFeatured: (
    project: ProjectAdminRead
  ) => void
}

function statusClass(
  status: string
): string {
  if (
    status === "published"
  ) {
    return "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400"
  }

  if (
    status === "archived"
  ) {
    return "bg-muted text-muted-foreground"
  }

  return "bg-amber-500/10 text-amber-700 dark:text-amber-400"
}

export function AdminProjectCard({
  project,
  busyAction,
  onToggleVisibility,
  onToggleFeatured,
}: AdminProjectCardProps) {
  const deleted =
    project.deleted_at !== null

  const canFeature =
    project.status ===
      "published" &&
    project.visibility ===
      "public" &&
    !deleted

  return (
    <article
      className={cn(
        "rounded-2xl border border-border bg-background p-5",
        deleted &&
          "opacity-70"
      )}
    >
      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
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

          <h2 className="mt-4 truncate text-lg font-semibold">
            {project.title}
          </h2>

          <p className="mt-1 truncate text-sm text-muted-foreground">
            /{project.slug}
          </p>

          <p className="mt-3 line-clamp-2 max-w-3xl text-sm leading-6 text-muted-foreground">
            {
              project.short_description
            }
          </p>

          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
            <span>
              Category:{" "}
              <strong className="font-medium text-foreground">
                {project.category
                  ?.name ??
                  "None"}
              </strong>
            </span>

            <span>
              Technologies:{" "}
              <strong className="font-medium text-foreground">
                {
                  project
                    .technology_assignments
                    .length
                }
              </strong>
            </span>

            <span>
              Order:{" "}
              <strong className="font-medium text-foreground">
                {
                  project.sort_order
                }
              </strong>
            </span>
          </div>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={
              deleted ||
              busyAction !== null
            }
            onClick={() =>
              onToggleVisibility(
                project
              )
            }
          >
            {busyAction ===
            "visibility" ? (
              <Loader2
                className="animate-spin"
                aria-hidden="true"
              />
            ) : project.visibility ===
              "public" ? (
              <EyeOff
                aria-hidden="true"
              />
            ) : (
              <Eye
                aria-hidden="true"
              />
            )}

            {project.visibility ===
            "public"
              ? "Make private"
              : "Make public"}
          </Button>

          <Button
            type="button"
            variant={
              project.is_featured
                ? "secondary"
                : "outline"
            }
            size="sm"
            disabled={
              !canFeature ||
              busyAction !== null
            }
            onClick={() =>
              onToggleFeatured(
                project
              )
            }
            title={
              canFeature
                ? undefined
                : "Only published public projects can be featured."
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
              : "Feature"}
          </Button>

          {!deleted ? (
            <Button
              asChild
              variant="ghost"
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

                View
              </Link>
            </Button>
          ) : null}
        </div>
      </div>
    </article>
  )
}