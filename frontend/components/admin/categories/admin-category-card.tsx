"use client"

import {
  FolderTree,
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
  ProjectCategoryAdminRead,
} from "@/types/portfolio/project-category"

export type CategoryBusyAction =
  | "status"
  | "delete"
  | "restore"

type AdminCategoryCardProps = {
  category:
    ProjectCategoryAdminRead

  selected:
    boolean

  busyAction:
    CategoryBusyAction | null

  onEdit: (
    category:
      ProjectCategoryAdminRead
  ) => void

  onToggleStatus: (
    category:
      ProjectCategoryAdminRead
  ) => void

  onDelete: (
    category:
      ProjectCategoryAdminRead
  ) => void

  onRestore: (
    category:
      ProjectCategoryAdminRead
  ) => void
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

export function AdminCategoryCard({
  category,
  selected,
  busyAction,
  onEdit,
  onToggleStatus,
  onDelete,
  onRestore,
}: AdminCategoryCardProps) {
  const deleted =
    category.deleted_at !==
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
                category.color
                  ? {
                      backgroundColor:
                        `${category.color}18`,
                    }
                  : undefined
              }
            >
              <FolderTree
                className="size-5"
                style={
                  category.color
                    ? {
                        color:
                          category.color,
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
                    category.name
                  }
                </h2>

                <span
                  className={
                    category.is_active
                      ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-400"
                      : "rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
                  }
                >
                  {category.is_active
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
                  category.slug
                }
              </p>

              {category.description ? (
                <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                  {
                    category.description
                  }
                </p>
              ) : null}

              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
                <span>
                  Sort order:{" "}
                  {
                    category.sort_order
                  }
                </span>

                {category.icon ? (
                  <span>
                    Icon:{" "}
                    {
                      category.icon
                    }
                  </span>
                ) : null}

                <span>
                  Updated:{" "}
                  {formatDate(
                    category.updated_at
                  )}
                </span>
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
                category
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
                    category
                  )
                }
              >
                {busyAction ===
                "status" ? (
                  <Loader2
                    className="animate-spin"
                    aria-hidden="true"
                  />
                ) : category.is_active ? (
                  <PowerOff
                    aria-hidden="true"
                  />
                ) : (
                  <Power
                    aria-hidden="true"
                  />
                )}

                {category.is_active
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
                    category
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
                  category
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