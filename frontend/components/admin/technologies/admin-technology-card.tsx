"use client"

import {
  Cpu,
  ExternalLink,
  Loader2,
  Pencil,
  Power,
  PowerOff,
  RotateCcw,
  Trash2,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import type {
  ProjectTechnologyCategory,
} from "@/types/portfolio/common"

import type {
  ProjectTechnologyAdminRead,
} from "@/types/portfolio/project-technology"

export type TechnologyBusyAction =
  | "status"
  | "delete"
  | "restore"

type AdminTechnologyCardProps = {
  technology:
    ProjectTechnologyAdminRead

  selected:
    boolean

  busyAction:
    TechnologyBusyAction | null

  onEdit: (
    technology:
      ProjectTechnologyAdminRead
  ) => void

  onToggleStatus: (
    technology:
      ProjectTechnologyAdminRead
  ) => void

  onDelete: (
    technology:
      ProjectTechnologyAdminRead
  ) => void

  onRestore: (
    technology:
      ProjectTechnologyAdminRead
  ) => void
}

const categoryLabels:
  Record<
    ProjectTechnologyCategory,
    string
  > = {
    language:
      "Language",

    framework:
      "Framework",

    library:
      "Library",

    database:
      "Database",

    platform:
      "Platform",

    cloud:
      "Cloud",

    devops:
      "DevOps",

    testing:
      "Testing",

    tool:
      "Tool",

    service:
      "Service",

    other:
      "Other",
  }

function formatDate(
  value:
    string
): string {
  const date =
    new Date(
      value
    )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }

  return date.toLocaleDateString()
}

export function AdminTechnologyCard({
  technology,
  selected,
  busyAction,
  onEdit,
  onToggleStatus,
  onDelete,
  onRestore,
}: AdminTechnologyCardProps) {
  const deleted =
    technology.deleted_at !==
    null

  const busy =
    busyAction !==
    null

  return (
    <article
      className={
        selected
          ? "rounded-2xl border border-primary/50 bg-primary/[0.03] p-5 shadow-sm"
          : "rounded-2xl border border-border bg-background p-5"
      }
    >
      <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div className="min-w-0">
          <div className="flex items-start gap-3">
            <div
              className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-border"
              style={
                technology.color
                  ? {
                      backgroundColor:
                        `${technology.color}18`,
                    }
                  : undefined
              }
            >
              <Cpu
                className="size-5"
                style={
                  technology.color
                    ? {
                        color:
                          technology.color,
                      }
                    : undefined
                }
                aria-hidden="true"
              />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="truncate text-lg font-semibold">
                  {
                    technology.name
                  }
                </h2>

                <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                  {
                    categoryLabels[
                      technology.category
                    ]
                  }
                </span>

                <span
                  className={
                    technology.is_active
                      ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-400"
                      : "rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
                  }
                >
                  {technology.is_active
                    ? "Active"
                    : "Inactive"}
                </span>

                {deleted ? (
                  <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                    Deleted
                  </span>
                ) : null}
              </div>

              <p className="mt-1 font-mono text-xs text-muted-foreground">
                /{
                  technology.slug
                }
              </p>

              {technology.description ? (
                <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                  {
                    technology.description
                  }
                </p>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
                <span>
                  Sort order:{" "}
                  {
                    technology.sort_order
                  }
                </span>

                {technology.icon ? (
                  <span>
                    Icon:{" "}
                    {
                      technology.icon
                    }
                  </span>
                ) : null}

                <span>
                  Updated:{" "}
                  {formatDate(
                    technology.updated_at
                  )}
                </span>

                {technology.official_url ? (
                  <a
                    href={
                      technology.official_url
                    }
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
                  >
                    Official site

                    <ExternalLink
                      className="size-3"
                      aria-hidden="true"
                    />
                  </a>
                ) : null}
              </div>
            </div>
          </div>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={
              busy ||
              deleted
            }
            onClick={() =>
              onEdit(
                technology
              )
            }
          >
            <Pencil
              aria-hidden="true"
            />

            Edit
          </Button>

          {!deleted ? (
            <>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={
                  busy
                }
                onClick={() =>
                  onToggleStatus(
                    technology
                  )
                }
              >
                {busyAction ===
                "status" ? (
                  <Loader2
                    className="animate-spin"
                    aria-hidden="true"
                  />
                ) : technology.is_active ? (
                  <PowerOff
                    aria-hidden="true"
                  />
                ) : (
                  <Power
                    aria-hidden="true"
                  />
                )}

                {technology.is_active
                  ? "Deactivate"
                  : "Activate"}
              </Button>

              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={
                  busy
                }
                onClick={() =>
                  onDelete(
                    technology
                  )
                }
              >
                {busyAction ===
                "delete" ? (
                  <Loader2
                    className="animate-spin"
                    aria-hidden="true"
                  />
                ) : (
                  <Trash2
                    aria-hidden="true"
                  />
                )}

                Delete
              </Button>
            </>
          ) : (
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={
                busy
              }
              onClick={() =>
                onRestore(
                  technology
                )
              }
            >
              {busyAction ===
              "restore" ? (
                <Loader2
                  className="animate-spin"
                  aria-hidden="true"
                />
              ) : (
                <RotateCcw
                  aria-hidden="true"
                />
              )}

              Restore
            </Button>
          )}
        </div>
      </div>
    </article>
  )
}