"use client"

import {
  useState,
  type FormEvent,
} from "react"

import type {
  ContactInquiryAdminRead,
  ContactInquiryAssigneeOption,
  ContactInquiryPriority,
  ContactInquiryProjectOption,
  ContactInquiryStatus,
  ContactInquiryType,
  ContactInquiryUpdate,
} from "@/types/contact"

export type InquiryBusyAction =
  | "update"
  | "read-state"
  | "status"
  | "delete"
  | "restore"

type AdminInquiryDetailProps = {
  inquiry: ContactInquiryAdminRead

  assignees:
    ContactInquiryAssigneeOption[]

  projects:
    ContactInquiryProjectOption[]

  busyAction:
    InquiryBusyAction | null

  onSave: (
    payload: ContactInquiryUpdate
  ) => Promise<void>

  onReadState: (
    isRead: boolean
  ) => Promise<void>

  onStatus: (
    status: ContactInquiryStatus
  ) => Promise<void>

  onDelete:
    () => Promise<void>

  onRestore:
    () => Promise<void>
}

const allowedStatusTransitions: Record<
  ContactInquiryStatus,
  ContactInquiryStatus[]
> = {
  new: [
    "in_progress",
    "responded",
    "closed",
    "spam",
  ],

  in_progress: [
    "new",
    "responded",
    "closed",
    "spam",
  ],

  responded: [
    "in_progress",
    "closed",
    "spam",
  ],

  closed: [
    "in_progress",
    "spam",
  ],

  spam: [
    "new",
    "in_progress",
  ],
}

const inquiryTypeOptions: ContactInquiryType[] = [
  "general",
  "employment",
  "freelance",
  "contract",
  "collaboration",
  "project",
  "support",
  "other",
]

const priorityOptions: ContactInquiryPriority[] = [
  "low",
  "normal",
  "high",
  "urgent",
]

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

function formatDateTime(
  value: string | null
): string {
  if (!value) {
    return "—"
  }

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

const fieldClassName =
  "mt-2 h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60"

export function AdminInquiryDetail({
  inquiry,
  assignees,
  projects,
  busyAction,
  onSave,
  onReadState,
  onStatus,
  onDelete,
  onRestore,
}: AdminInquiryDetailProps) {
  const [
    priority,
    setPriority,
  ] =
    useState<ContactInquiryPriority>(
      inquiry.priority
    )

  const [
    inquiryType,
    setInquiryType,
  ] =
    useState<ContactInquiryType>(
      inquiry.inquiry_type
    )

  const [
    assignedToId,
    setAssignedToId,
  ] =
    useState(
      inquiry.assigned_to_id ??
        ""
    )

  const [
    internalNotes,
    setInternalNotes,
  ] =
    useState(
      inquiry.internal_notes ??
        ""
    )

  const [
    statusTarget,
    setStatusTarget,
  ] =
    useState<ContactInquiryStatus>(
      inquiry.status
    )

  const isBusy =
    busyAction !== null

  const deleted =
    Boolean(
      inquiry.deleted_at
    )

  const assignee =
    assignees.find(
      (candidate) =>
        candidate.id ===
        inquiry.assigned_to_id
    )

  const project =
    projects.find(
      (candidate) =>
        candidate.id ===
        inquiry.project_id
    )

  const replyHref =
    `mailto:${encodeURIComponent(
      inquiry.email
    )}?subject=${encodeURIComponent(
      `Re: ${inquiry.subject}`
    )}`

  async function handleSave(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    await onSave({
      priority,

      inquiry_type:
        inquiryType,

      assigned_to_id:
        assignedToId ||
        null,

      internal_notes:
        internalNotes.trim() ||
        null,
    })
  }

  return (
    <section className="rounded-2xl border border-border/70 bg-card shadow-sm">
      <div className="border-b border-border/70 p-5 sm:p-6">
        <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h2 className="text-xl font-bold tracking-tight">
                {inquiry.subject}
              </h2>

              {!inquiry.is_read ? (
                <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                  Unread
                </span>
              ) : null}

              {deleted ? (
                <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                  Deleted
                </span>
              ) : null}
            </div>

            <p className="mt-2 text-sm text-muted-foreground">
              Received{" "}
              {formatDateTime(
                inquiry.created_at
              )}
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <a
              href={replyHref}
              className="inline-flex h-9 items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium transition-colors hover:bg-muted"
            >
              Reply by email
            </a>

            {!deleted ? (
              <button
                type="button"
                disabled={isBusy}
                onClick={() => {
                  void onReadState(
                    !inquiry.is_read
                  )
                }}
                className="inline-flex h-9 items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50"
              >
                {busyAction ===
                "read-state"
                  ? "Updating..."
                  : inquiry.is_read
                    ? "Mark unread"
                    : "Mark read"}
              </button>
            ) : null}
          </div>
        </div>
      </div>

      <div className="grid gap-6 p-5 sm:p-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="space-y-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Sender
            </p>

            <p className="mt-2 font-semibold">
              {inquiry.name}
            </p>

            <div className="mt-2 space-y-1 text-sm">
              <p>
                <a
                  href={`mailto:${inquiry.email}`}
                  className="text-primary hover:underline"
                >
                  {inquiry.email}
                </a>
              </p>

              {inquiry.phone ? (
                <p>
                  <a
                    href={`tel:${inquiry.phone}`}
                    className="hover:underline"
                  >
                    {inquiry.phone}
                  </a>
                </p>
              ) : null}

              {inquiry.company ? (
                <p className="text-muted-foreground">
                  {inquiry.company}
                </p>
              ) : null}
            </div>
          </div>

          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Message
            </p>

            <div className="mt-3 whitespace-pre-wrap rounded-xl border border-border/70 bg-muted/30 p-4 text-sm leading-7">
              {inquiry.message}
            </div>
          </div>

          <form
            onSubmit={handleSave}
            className="space-y-5"
          >
            <div className="border-t border-border/70 pt-5">
              <h3 className="font-semibold">
                Administrative
                details
              </h3>

              <p className="mt-1 text-sm text-muted-foreground">
                Update
                classification,
                priority,
                assignment and
                private notes.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label
                  htmlFor="inquiry-detail-type"
                  className="text-sm font-medium"
                >
                  Inquiry type
                </label>

                <select
                  id="inquiry-detail-type"
                  value={inquiryType}
                  disabled={
                    deleted ||
                    isBusy
                  }
                  onChange={(
                    event
                  ) => {
                    setInquiryType(
                      event
                        .target
                        .value as ContactInquiryType
                    )
                  }}
                  className={
                    fieldClassName
                  }
                >
                  {inquiryTypeOptions.map(
                    (value) => (
                      <option
                        key={value}
                        value={value}
                      >
                        {humanize(
                          value
                        )}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div>
                <label
                  htmlFor="inquiry-detail-priority"
                  className="text-sm font-medium"
                >
                  Priority
                </label>

                <select
                  id="inquiry-detail-priority"
                  value={priority}
                  disabled={
                    deleted ||
                    isBusy
                  }
                  onChange={(
                    event
                  ) => {
                    setPriority(
                      event
                        .target
                        .value as ContactInquiryPriority
                    )
                  }}
                  className={
                    fieldClassName
                  }
                >
                  {priorityOptions.map(
                    (value) => (
                      <option
                        key={value}
                        value={value}
                      >
                        {humanize(
                          value
                        )}
                      </option>
                    )
                  )}
                </select>
              </div>
            </div>

            <div>
              <label
                htmlFor="inquiry-detail-assignee"
                className="text-sm font-medium"
              >
                Assigned to
              </label>

              <select
                id="inquiry-detail-assignee"
                value={
                  assignedToId
                }
                disabled={
                  deleted ||
                  isBusy
                }
                onChange={(
                  event
                ) => {
                  setAssignedToId(
                    event.target
                      .value
                  )
                }}
                className={
                  fieldClassName
                }
              >
                <option value="">
                  Unassigned
                </option>

                {assignees.map(
                  (option) => (
                    <option
                      key={
                        option.id
                      }
                      value={
                        option.id
                      }
                    >
                      {
                        option.full_name
                      }{" "}
                      ({
                        option.email
                      })
                    </option>
                  )
                )}
              </select>
            </div>

            <div>
              <label
                htmlFor="inquiry-internal-notes"
                className="text-sm font-medium"
              >
                Internal notes
              </label>

              <textarea
                id="inquiry-internal-notes"
                rows={5}
                maxLength={
                  10_000
                }
                value={
                  internalNotes
                }
                disabled={
                  deleted ||
                  isBusy
                }
                onChange={(
                  event
                ) => {
                  setInternalNotes(
                    event.target
                      .value
                  )
                }}
                placeholder="Private notes for administrators..."
                className="mt-2 w-full resize-y rounded-lg border border-input bg-background px-3 py-3 text-sm leading-6 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </div>

            {!deleted ? (
              <button
                type="submit"
                disabled={isBusy}
                className="inline-flex h-10 items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground transition-opacity disabled:pointer-events-none disabled:opacity-50"
              >
                {busyAction ===
                "update"
                  ? "Saving..."
                  : "Save changes"}
              </button>
            ) : null}
          </form>

          <details className="rounded-xl border border-border/70 bg-muted/20 p-4">
            <summary className="cursor-pointer text-sm font-medium">
              Submission metadata
            </summary>

            <div className="mt-4 space-y-3 break-all text-xs leading-5 text-muted-foreground">
              <p>
                Consent:{" "}
                {inquiry.consent_given
                  ? "Given"
                  : "Not given"}
              </p>

              <p>
                Source page:{" "}
                {inquiry.source_page ??
                  "—"}
              </p>

              <p>
                User agent:{" "}
                {inquiry.user_agent ??
                  "—"}
              </p>

              <p>
                IP hash:{" "}
                {inquiry.ip_address_hash ??
                  "—"}
              </p>

              <p>
                Submission
                fingerprint:{" "}
                {inquiry.submission_fingerprint ??
                  "—"}
              </p>
            </div>
          </details>
        </div>

        <aside className="space-y-5">
          <div className="rounded-xl border border-border/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Workflow
            </p>

            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Status
                </dt>

                <dd className="font-medium">
                  {humanize(
                    inquiry.status
                  )}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Priority
                </dt>

                <dd className="font-medium">
                  {humanize(
                    inquiry.priority
                  )}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Read
                </dt>

                <dd>
                  {inquiry.is_read
                    ? "Yes"
                    : "No"}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Read at
                </dt>

                <dd className="text-right">
                  {formatDateTime(
                    inquiry.read_at
                  )}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Responded
                </dt>

                <dd className="text-right">
                  {formatDateTime(
                    inquiry.responded_at
                  )}
                </dd>
              </div>

              <div className="flex justify-between gap-4">
                <dt className="text-muted-foreground">
                  Closed
                </dt>

                <dd className="text-right">
                  {formatDateTime(
                    inquiry.closed_at
                  )}
                </dd>
              </div>
            </dl>
          </div>

          <div className="rounded-xl border border-border/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
              Context
            </p>

            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="text-muted-foreground">
                  Assignee
                </dt>

                <dd className="mt-1 font-medium">
                  {assignee
                    ? `${assignee.full_name} (${assignee.email})`
                    : inquiry.assigned_to_id
                      ? inquiry.assigned_to_id
                      : "Unassigned"}
                </dd>
              </div>

              <div>
                <dt className="text-muted-foreground">
                  Related
                  project
                </dt>

                <dd className="mt-1 font-medium">
                  {project
                    ? project.title
                    : inquiry.project_id ??
                      "None"}
                </dd>
              </div>

              <div>
                <dt className="text-muted-foreground">
                  Updated
                </dt>

                <dd className="mt-1">
                  {formatDateTime(
                    inquiry.updated_at
                  )}
                </dd>
              </div>
            </dl>
          </div>

          {!deleted ? (
            <div className="rounded-xl border border-border/70 p-4">
              <label
                htmlFor="inquiry-status-target"
                className="text-sm font-medium"
              >
                Change status
              </label>

              <select
                id="inquiry-status-target"
                value={
                  statusTarget
                }
                disabled={isBusy}
                onChange={(
                  event
                ) => {
                  setStatusTarget(
                    event
                      .target
                      .value as ContactInquiryStatus
                  )
                }}
                className={
                  fieldClassName
                }
              >
                <option
                  value={
                    inquiry.status
                  }
                >
                  {humanize(
                    inquiry.status
                  )}{" "}
                  (current)
                </option>

                {allowedStatusTransitions[
                  inquiry.status
                ].map(
                  (status) => (
                    <option
                      key={
                        status
                      }
                      value={
                        status
                      }
                    >
                      {humanize(
                        status
                      )}
                    </option>
                  )
                )}
              </select>

              <button
                type="button"
                disabled={
                  isBusy ||
                  statusTarget ===
                    inquiry.status
                }
                onClick={() => {
                  void onStatus(
                    statusTarget
                  )
                }}
                className="mt-3 inline-flex h-9 w-full items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50"
              >
                {busyAction ===
                "status"
                  ? "Updating status..."
                  : "Apply status"}
              </button>
            </div>
          ) : null}

          {deleted ? (
            <button
              type="button"
              disabled={isBusy}
              onClick={() => {
                void onRestore()
              }}
              className="inline-flex h-10 w-full items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground disabled:pointer-events-none disabled:opacity-50"
            >
              {busyAction ===
              "restore"
                ? "Restoring..."
                : "Restore inquiry"}
            </button>
          ) : (
            <button
              type="button"
              disabled={isBusy}
              onClick={() => {
                void onDelete()
              }}
              className="inline-flex h-10 w-full items-center justify-center rounded-lg border border-destructive/40 bg-destructive/5 px-4 text-sm font-medium text-destructive transition-colors hover:bg-destructive/10 disabled:pointer-events-none disabled:opacity-50"
            >
              {busyAction ===
              "delete"
                ? "Deleting..."
                : "Delete inquiry"}
            </button>
          )}
        </aside>
      </div>
    </section>
  )
}