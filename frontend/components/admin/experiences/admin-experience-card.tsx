"use client"

import {
  BriefcaseBusiness,
  Building2,
  ExternalLink,
  MapPin,
  Pencil,
} from "lucide-react"

import {
  AdminExperienceLifecycle,
  type ExperienceBusyAction,
} from "@/components/admin/experiences/admin-experience-lifecycle"

import {
  Button,
} from "@/components/ui/button"

import type {
  EmploymentType,
  ExperienceAdminRead,
  ExperienceLocationType,
} from "@/types/portfolio/experience"

type AdminExperienceCardProps = {
  experience:
    ExperienceAdminRead

  selected:
    boolean

  busyAction:
    ExperienceBusyAction | null

  onEdit: (
    experience:
      ExperienceAdminRead
  ) => void

  onToggleVisibility: (
    experience:
      ExperienceAdminRead
  ) => void

  onToggleFeatured: (
    experience:
      ExperienceAdminRead
  ) => void

  onDelete: (
    experience:
      ExperienceAdminRead
  ) => void

  onRestore: (
    experience:
      ExperienceAdminRead
  ) => void
}

const employmentLabels:
  Record<
    EmploymentType,
    string
  > = {
    full_time:
      "Full-time",

    part_time:
      "Part-time",

    contract:
      "Contract",

    freelance:
      "Freelance",

    internship:
      "Internship",

    apprenticeship:
      "Apprenticeship",

    temporary:
      "Temporary",

    volunteer:
      "Volunteer",

    self_employed:
      "Self-employed",

    other:
      "Other",
  }

const locationLabels:
  Record<
    ExperienceLocationType,
    string
  > = {
    onsite:
      "On-site",

    remote:
      "Remote",

    hybrid:
      "Hybrid",
  }

function formatMonthYear(
  value:
    string
): string {
  const date =
    new Date(
      `${value}T00:00:00Z`
    )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      month:
        "short",

      year:
        "numeric",

      timeZone:
        "UTC",
    }
  ).format(
    date
  )
}

function formatUpdated(
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

export function AdminExperienceCard({
  experience,
  selected,
  busyAction,
  onEdit,
  onToggleVisibility,
  onToggleFeatured,
  onDelete,
  onRestore,
}: AdminExperienceCardProps) {
  const deleted =
    experience.deleted_at !==
    null

  const busy =
    busyAction !==
    null

  const start =
    formatMonthYear(
      experience.start_date
    )

  const end =
    experience.is_current
      ? "Present"
      : experience.end_date
        ? formatMonthYear(
            experience.end_date
          )
        : null

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
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl border border-border bg-muted/30">
              <BriefcaseBusiness
                className="size-5 text-primary"
                aria-hidden="true"
              />
            </div>

            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-lg font-semibold">
                  {
                    experience.job_title
                  }
                </h2>

                {experience.is_current ? (
                  <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-medium text-primary">
                    Current
                  </span>
                ) : (
                  <span className="rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
                    Completed
                  </span>
                )}

                <span
                  className={
                    experience.is_public
                      ? "rounded-full bg-emerald-500/10 px-2.5 py-1 text-xs font-medium text-emerald-700 dark:text-emerald-400"
                      : "rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
                  }
                >
                  {experience.is_public
                    ? "Public"
                    : "Private"}
                </span>

                {experience.is_featured ? (
                  <span className="rounded-full bg-amber-500/10 px-2.5 py-1 text-xs font-medium text-amber-700 dark:text-amber-400">
                    Featured
                  </span>
                ) : null}

                {deleted ? (
                  <span className="rounded-full bg-destructive/10 px-2.5 py-1 text-xs font-medium text-destructive">
                    Deleted
                  </span>
                ) : null}
              </div>

              <div className="mt-2 flex items-center gap-2 text-sm font-medium">
                <Building2
                  className="size-4 text-muted-foreground"
                  aria-hidden="true"
                />

                {
                  experience.company_name
                }
              </div>

              <p className="mt-1 font-mono text-xs text-muted-foreground">
                /{
                  experience.slug
                }
              </p>

              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-muted-foreground">
                <span>
                  {start}

                  {end
                    ? ` — ${end}`
                    : ""}
                </span>

                <span>
                  {
                    employmentLabels[
                      experience.employment_type
                    ]
                  }
                </span>

                <span>
                  {
                    locationLabels[
                      experience.location_type
                    ]
                  }
                </span>

                {experience.location ? (
                  <span className="inline-flex items-center gap-1">
                    <MapPin
                      className="size-3"
                      aria-hidden="true"
                    />

                    {
                      experience.location
                    }
                  </span>
                ) : null}

                <span>
                  Sort:{" "}
                  {
                    experience.sort_order
                  }
                </span>

                <span>
                  Updated:{" "}
                  {formatUpdated(
                    experience.updated_at
                  )}
                </span>

                {experience.company_website ? (
                  <a
                    href={
                      experience.company_website
                    }
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 font-medium text-primary hover:underline"
                  >
                    Company

                    <ExternalLink
                      className="size-3"
                      aria-hidden="true"
                    />
                  </a>
                ) : null}
              </div>

              <p className="mt-4 max-w-3xl text-sm leading-6 text-muted-foreground">
                {
                  experience.summary
                }
              </p>
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
                experience
              )
            }
          >
            <Pencil
              aria-hidden="true"
            />

            Edit
          </Button>

          <AdminExperienceLifecycle
            experience={
              experience
            }
            busyAction={
              busyAction
            }
            onToggleVisibility={
              onToggleVisibility
            }
            onToggleFeatured={
              onToggleFeatured
            }
            onDelete={
              onDelete
            }
            onRestore={
              onRestore
            }
          />
        </div>
      </div>
    </article>
  )
}