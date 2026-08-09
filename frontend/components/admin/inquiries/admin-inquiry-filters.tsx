"use client"

import type {
  ContactInquiryAssigneeOption,
  ContactInquiryProjectOption,
} from "@/types/contact"

import {
  defaultInquiryAdminFilters,
  type InquiryAdminFilters,
} from "./inquiry-admin-filters"

type AdminInquiryFiltersProps = {
  filters:
    InquiryAdminFilters

  assignees:
    ContactInquiryAssigneeOption[]

  projects:
    ContactInquiryProjectOption[]

  disabled?: boolean

  onChange:
    (
      filters:
        InquiryAdminFilters
    ) => void
}

const inquiryTypeOptions = [
  [
    "general",
    "General",
  ],
  [
    "employment",
    "Employment",
  ],
  [
    "freelance",
    "Freelance",
  ],
  [
    "contract",
    "Contract",
  ],
  [
    "collaboration",
    "Collaboration",
  ],
  [
    "project",
    "Project",
  ],
  [
    "support",
    "Support",
  ],
  [
    "other",
    "Other",
  ],
] as const

const statusOptions = [
  [
    "new",
    "New",
  ],
  [
    "in_progress",
    "In progress",
  ],
  [
    "responded",
    "Responded",
  ],
  [
    "closed",
    "Closed",
  ],
  [
    "spam",
    "Spam",
  ],
] as const

const priorityOptions = [
  [
    "low",
    "Low",
  ],
  [
    "normal",
    "Normal",
  ],
  [
    "high",
    "High",
  ],
  [
    "urgent",
    "Urgent",
  ],
] as const

const sortOptions = [
  [
    "created_at",
    "Received",
  ],
  [
    "updated_at",
    "Updated",
  ],
  [
    "name",
    "Sender name",
  ],
  [
    "email",
    "Email",
  ],
  [
    "subject",
    "Subject",
  ],
  [
    "inquiry_type",
    "Inquiry type",
  ],
  [
    "status",
    "Status",
  ],
  [
    "priority",
    "Priority",
  ],
  [
    "is_read",
    "Read state",
  ],
] as const

const fieldClassName =
  "h-10 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"

export function AdminInquiryFilters({
  filters,
  assignees,
  projects,
  disabled = false,
  onChange,
}: AdminInquiryFiltersProps) {
  function update<
    K extends keyof InquiryAdminFilters,
  >(
    key: K,
    value:
      InquiryAdminFilters[K]
  ) {
    onChange({
      ...filters,
      [key]:
        value,
    })
  }

  function resetFilters() {
    onChange({
      ...defaultInquiryAdminFilters,
    })
  }

  return (
    <section className="rounded-2xl border border-border/70 bg-card p-4 shadow-sm sm:p-5">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
        <div>
          <h2 className="font-semibold">
            Search and filters
          </h2>

          <p className="mt-1 text-sm text-muted-foreground">
            Narrow the inbox by
            sender, workflow,
            assignment, project or
            date.
          </p>
        </div>

        <button
          type="button"
          disabled={disabled}
          onClick={
            resetFilters
          }
          className="inline-flex h-9 items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium transition-colors hover:bg-muted disabled:pointer-events-none disabled:opacity-50"
        >
          Reset filters
        </button>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="md:col-span-2 xl:col-span-4">
          <label
            htmlFor="inquiry-search"
            className="text-sm font-medium"
          >
            Search
          </label>

          <input
            id="inquiry-search"
            type="search"
            value={
              filters.search
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "search",
                event.target
                  .value
              )
            }}
            placeholder="Name, email, phone, company, subject, message or notes"
            className={`mt-2 ${fieldClassName}`}
          />
        </div>

        <div>
          <label
            htmlFor="inquiry-type-filter"
            className="text-sm font-medium"
          >
            Inquiry type
          </label>

          <select
            id="inquiry-type-filter"
            value={
              filters.inquiryType
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "inquiryType",
                event.target
                  .value as InquiryAdminFilters["inquiryType"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All types
            </option>

            {inquiryTypeOptions.map(
              ([
                value,
                label,
              ]) => (
                <option
                  key={
                    value
                  }
                  value={
                    value
                  }
                >
                  {label}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-status-filter"
            className="text-sm font-medium"
          >
            Status
          </label>

          <select
            id="inquiry-status-filter"
            value={
              filters.status
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "status",
                event.target
                  .value as InquiryAdminFilters["status"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All statuses
            </option>

            {statusOptions.map(
              ([
                value,
                label,
              ]) => (
                <option
                  key={
                    value
                  }
                  value={
                    value
                  }
                >
                  {label}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-priority-filter"
            className="text-sm font-medium"
          >
            Priority
          </label>

          <select
            id="inquiry-priority-filter"
            value={
              filters.priority
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "priority",
                event.target
                  .value as InquiryAdminFilters["priority"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All priorities
            </option>

            {priorityOptions.map(
              ([
                value,
                label,
              ]) => (
                <option
                  key={
                    value
                  }
                  value={
                    value
                  }
                >
                  {label}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-read-filter"
            className="text-sm font-medium"
          >
            Read state
          </label>

          <select
            id="inquiry-read-filter"
            value={
              filters.readState
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "readState",
                event.target
                  .value as InquiryAdminFilters["readState"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All messages
            </option>

            <option value="unread">
              Unread
            </option>

            <option value="read">
              Read
            </option>
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-assignee-filter"
            className="text-sm font-medium"
          >
            Assignment
          </label>

          <select
            id="inquiry-assignee-filter"
            value={
              filters.assignment
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "assignment",
                event.target
                  .value
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All assignments
            </option>

            <option value="unassigned">
              Unassigned
            </option>

            {assignees.map(
              (
                assignee
              ) => (
                <option
                  key={
                    assignee.id
                  }
                  value={
                    assignee.id
                  }
                >
                  {
                    assignee.full_name
                  }{" "}
                  ({
                    assignee.email
                  })
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-project-filter"
            className="text-sm font-medium"
          >
            Related project
          </label>

          <select
            id="inquiry-project-filter"
            value={
              filters.project
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "project",
                event.target
                  .value
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="all">
              All projects
            </option>

            {projects.map(
              (
                project
              ) => (
                <option
                  key={
                    project.id
                  }
                  value={
                    project.id
                  }
                >
                  {
                    project.title
                  }
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-created-from"
            className="text-sm font-medium"
          >
            Received from
          </label>

          <input
            id="inquiry-created-from"
            type="date"
            value={
              filters.createdFrom
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "createdFrom",
                event.target
                  .value
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          />
        </div>

        <div>
          <label
            htmlFor="inquiry-created-to"
            className="text-sm font-medium"
          >
            Received to
          </label>

          <input
            id="inquiry-created-to"
            type="date"
            value={
              filters.createdTo
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "createdTo",
                event.target
                  .value
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          />
        </div>

        <div>
          <label
            htmlFor="inquiry-sort"
            className="text-sm font-medium"
          >
            Sort by
          </label>

          <select
            id="inquiry-sort"
            value={
              filters.sortBy
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "sortBy",
                event.target
                  .value as InquiryAdminFilters["sortBy"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            {sortOptions.map(
              ([
                value,
                label,
              ]) => (
                <option
                  key={
                    value
                  }
                  value={
                    value
                  }
                >
                  {label}
                </option>
              )
            )}
          </select>
        </div>

        <div>
          <label
            htmlFor="inquiry-sort-direction"
            className="text-sm font-medium"
          >
            Direction
          </label>

          <select
            id="inquiry-sort-direction"
            value={
              filters.sortDirection
            }
            disabled={
              disabled
            }
            onChange={(
              event
            ) => {
              update(
                "sortDirection",
                event.target
                  .value as InquiryAdminFilters["sortDirection"]
              )
            }}
            className={`mt-2 ${fieldClassName}`}
          >
            <option value="desc">
              Descending
            </option>

            <option value="asc">
              Ascending
            </option>
          </select>
        </div>
      </div>

      <label className="mt-5 flex items-center gap-3 text-sm">
        <input
          type="checkbox"
          checked={
            filters.includeDeleted
          }
          disabled={
            disabled
          }
          onChange={(
            event
          ) => {
            update(
              "includeDeleted",
              event.target
                .checked
            )
          }}
          className="size-4 rounded border-input"
        />

        Include deleted
        inquiries
      </label>
    </section>
  )
}