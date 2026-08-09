"use client"

import type {
  ContactInquirySummary,
} from "@/types/contact"

type AdminInquiryCardProps = {
  inquiry:
    ContactInquirySummary

  selected?: boolean

  assigneeName?: string

  projectTitle?: string

  disabled?: boolean

  onSelect:
    () => void
}

function formatDateTime(
  value: string
): string {
  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle:
        "medium",

      timeStyle:
        "short",
    }
  ).format(date)
}

function humanize(
  value: string
): string {
  return value
    .replaceAll(
      "_",
      " "
    )
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    )
}

export function AdminInquiryCard({
  inquiry,
  selected = false,
  assigneeName,
  projectTitle,
  disabled = false,
  onSelect,
}: AdminInquiryCardProps) {
  const deleted =
    Boolean(
      inquiry.deleted_at
    )

  return (
    <button
      type="button"
      disabled={
        disabled
      }
      onClick={
        onSelect
      }
      className={[
        "w-full rounded-2xl border p-4 text-left shadow-sm transition-colors",
        selected
          ? "border-primary bg-primary/5"
          : "border-border/70 bg-card hover:bg-muted/40",
        disabled
          ? "cursor-not-allowed opacity-70"
          : "",
      ].join(" ")}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            {!inquiry.is_read ? (
              <span className="size-2 shrink-0 rounded-full bg-primary" />
            ) : null}

            <p className="truncate font-semibold">
              {
                inquiry.name
              }
            </p>
          </div>

          <p className="mt-1 truncate text-sm text-muted-foreground">
            {
              inquiry.email
            }
          </p>
        </div>

        <span className="shrink-0 text-xs text-muted-foreground">
          {formatDateTime(
            inquiry.created_at
          )}
        </span>
      </div>

      <p className="mt-4 line-clamp-2 text-sm font-medium leading-6">
        {
          inquiry.subject
        }
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        <span className="rounded-full border border-border px-2.5 py-1 text-xs">
          {humanize(
            inquiry.status
          )}
        </span>

        <span className="rounded-full border border-border px-2.5 py-1 text-xs">
          {humanize(
            inquiry.priority
          )}
        </span>

        <span className="rounded-full border border-border px-2.5 py-1 text-xs">
          {humanize(
            inquiry.inquiry_type
          )}
        </span>

        <span className="rounded-full border border-border px-2.5 py-1 text-xs">
          {inquiry.is_read
            ? "Read"
            : "Unread"}
        </span>

        {deleted ? (
          <span className="rounded-full border border-destructive/30 bg-destructive/5 px-2.5 py-1 text-xs text-destructive">
            Deleted
          </span>
        ) : null}
      </div>

      <div className="mt-4 space-y-1 text-xs text-muted-foreground">
        <p>
          Assignee:{" "}
          <span className="text-foreground">
            {assigneeName ??
              "Unassigned"}
          </span>
        </p>

        {inquiry.project_id ? (
          <p>
            Project:{" "}
            <span className="text-foreground">
              {projectTitle ??
                inquiry.project_id}
            </span>
          </p>
        ) : null}
      </div>
    </button>
  )
}