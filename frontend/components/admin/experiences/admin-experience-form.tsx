"use client"

import {
  AlertCircle,
  Check,
  Loader2,
  Save,
  X,
} from "lucide-react"

import {
  useState,
  type FormEvent,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminExperienceService,
} from "@/services/admin"

import type {
  EmploymentType,
  ExperienceAdminRead,
  ExperienceCreate,
  ExperienceLocationType,
  ExperienceUpdate,
} from "@/types/portfolio/experience"

type AdminExperienceFormProps = {
  experience:
    ExperienceAdminRead | null

  mode:
    "create" | "edit"

  onSaved: (
    experience:
      ExperienceAdminRead,
    created:
      boolean
  ) => void

  onCancel: () => void
}

type ExperienceFormState = {
  companyName: string
  jobTitle: string
  slug: string

  employmentType:
    EmploymentType

  location: string

  locationType:
    ExperienceLocationType

  startDate: string
  endDate: string

  isCurrent: boolean

  summary: string
  responsibilities: string
  achievements: string

  companyWebsite: string
  companyLogoUrl: string

  sortOrder: string

  isPublic: boolean
  isFeatured: boolean
}

function slugify(
  value:
    string
): string {
  return value
    .trim()
    .toLowerCase()
    .replace(
      /[^a-z0-9]+/g,
      "-"
    )
    .replace(
      /^-+|-+$/g,
      ""
    )
}

function nullable(
  value:
    string
): string | null {
  const normalized =
    value.trim()

  return normalized
    ? normalized
    : null
}

function isValidUrl(
  value:
    string
): boolean {
  try {
    const url =
      new URL(
        value
      )

    return (
      url.protocol ===
        "http:" ||
      url.protocol ===
        "https:"
    )
  } catch {
    return false
  }
}

function experienceToForm(
  experience:
    ExperienceAdminRead | null
): ExperienceFormState {
  return {
    companyName:
      experience?.company_name ??
      "",

    jobTitle:
      experience?.job_title ??
      "",

    slug:
      experience?.slug ??
      "",

    employmentType:
      experience?.employment_type ??
      "full_time",

    location:
      experience?.location ??
      "",

    locationType:
      experience?.location_type ??
      "onsite",

    startDate:
      experience?.start_date ??
      "",

    endDate:
      experience?.end_date ??
      "",

    isCurrent:
      experience?.is_current ??
      false,

    summary:
      experience?.summary ??
      "",

    responsibilities:
      experience?.responsibilities ??
      "",

    achievements:
      experience?.achievements ??
      "",

    companyWebsite:
      experience?.company_website ??
      "",

    companyLogoUrl:
      experience?.company_logo_url ??
      "",

    sortOrder:
      String(
        experience?.sort_order ??
          0
      ),

    isPublic:
      experience?.is_public ??
      false,

    isFeatured:
      experience?.is_featured ??
      false,
  }
}

export function AdminExperienceForm({
  experience,
  mode,
  onSaved,
  onCancel,
}: AdminExperienceFormProps) {
  const [
    form,
    setForm,
  ] =
    useState<ExperienceFormState>(
      () =>
        experienceToForm(
          experience
        )
    )

  const [
    saving,
    setSaving,
  ] =
    useState(false)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  const [
    success,
    setSuccess,
  ] =
    useState<string | null>(
      null
    )

  const editing =
    mode ===
    "edit"

  function updateField<
    TKey extends keyof ExperienceFormState,
  >(
    key:
      TKey,
    value:
      ExperienceFormState[TKey]
  ) {
    setForm(
      (
        current
      ) => ({
        ...current,
        [key]:
          value,
      })
    )

    setError(
      null
    )

    setSuccess(
      null
    )
  }

  function updateSlug(
    value:
      string
  ) {
    updateField(
      "slug",
      slugify(
        value
      )
    )
  }

  function updateCurrent(
    value:
      boolean
  ) {
    setForm(
      (
        current
      ) => ({
        ...current,

        isCurrent:
          value,

        endDate:
          value
            ? ""
            : current.endDate,
      })
    )

    setError(
      null
    )

    setSuccess(
      null
    )
  }

  function updatePublic(
    value:
      boolean
  ) {
    setForm(
      (
        current
      ) => ({
        ...current,

        isPublic:
          value,

        isFeatured:
          value
            ? current.isFeatured
            : false,
      })
    )

    setError(
      null
    )

    setSuccess(
      null
    )
  }

  function buildCommonPayload() {
    const companyName =
      form.companyName.trim()

    const jobTitle =
      form.jobTitle.trim()

    const slug =
      slugify(
        form.slug
      )

    const summary =
      form.summary.trim()

    if (
      companyName.length <
      2
    ) {
      setError(
        "Company name must contain at least 2 characters."
      )

      return null
    }

    if (
      jobTitle.length <
      2
    ) {
      setError(
        "Job title must contain at least 2 characters."
      )

      return null
    }

    if (
      slug.length <
      2
    ) {
      setError(
        "Experience slug must contain at least 2 characters."
      )

      return null
    }

    if (
      !form.startDate
    ) {
      setError(
        "Start date is required."
      )

      return null
    }

    if (
      form.isCurrent &&
      form.endDate
    ) {
      setError(
        "A current experience cannot include an end date."
      )

      return null
    }

    if (
      form.endDate &&
      form.endDate <
        form.startDate
    ) {
      setError(
        "End date cannot be before the start date."
      )

      return null
    }

    if (
      summary.length <
      10
    ) {
      setError(
        "Summary must contain at least 10 characters."
      )

      return null
    }

    const sortOrder =
      Number(
        form.sortOrder
      )

    if (
      !Number.isInteger(
        sortOrder
      ) ||
      sortOrder <
        0
    ) {
      setError(
        "Sort order must be a whole number of 0 or greater."
      )

      return null
    }

    const companyWebsite =
      nullable(
        form.companyWebsite
      )

    if (
      companyWebsite &&
      !isValidUrl(
        companyWebsite
      )
    ) {
      setError(
        "Company website must be a valid HTTP or HTTPS URL."
      )

      return null
    }

    const companyLogoUrl =
      nullable(
        form.companyLogoUrl
      )

    if (
      companyLogoUrl &&
      !isValidUrl(
        companyLogoUrl
      )
    ) {
      setError(
        "Company logo URL must be a valid HTTP or HTTPS URL."
      )

      return null
    }

    return {
      company_name:
        companyName,

      job_title:
        jobTitle,

      slug,

      employment_type:
        form.employmentType,

      location:
        nullable(
          form.location
        ),

      location_type:
        form.locationType,

      start_date:
        form.startDate,

      end_date:
        form.isCurrent
          ? null
          : nullable(
              form.endDate
            ),

      is_current:
        form.isCurrent,

      summary,

      responsibilities:
        nullable(
          form.responsibilities
        ),

      achievements:
        nullable(
          form.achievements
        ),

      company_website:
        companyWebsite,

      company_logo_url:
        companyLogoUrl,

      sort_order:
        sortOrder,
    }
  }

  async function submit(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (
      saving
    ) {
      return
    }

    const commonPayload =
      buildCommonPayload()

    if (
      !commonPayload
    ) {
      return
    }

    try {
      setSaving(
        true
      )

      setError(
        null
      )

      setSuccess(
        null
      )

      let updated:
        ExperienceAdminRead

      if (
        editing &&
        experience
      ) {
        const payload:
          ExperienceUpdate = {
          ...commonPayload,
        }

        updated =
          await adminExperienceService.updateExperience(
            experience.id,
            payload
          )
      } else {
        const payload:
          ExperienceCreate = {
          ...commonPayload,

          is_public:
            form.isPublic,

          is_featured:
            form.isPublic
              ? form.isFeatured
              : false,
        }

        updated =
          await adminExperienceService.createExperience(
            payload
          )
      }

      setForm(
        experienceToForm(
          updated
        )
      )

      setSuccess(
        editing
          ? "Experience changes saved successfully."
          : "Experience created successfully."
      )

      onSaved(
        updated,
        !editing
      )
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : editing
            ? "The experience could not be updated."
            : "The experience could not be created."
      )
    } finally {
      setSaving(
        false
      )
    }
  }

  return (
    <form
      onSubmit={
        submit
      }
      className="rounded-2xl border border-border bg-background"
    >
      <div className="flex items-start justify-between gap-4 border-b border-border p-5 sm:p-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
            {editing
              ? "Edit experience"
              : "New experience"}
          </p>

          <h2 className="mt-2 text-xl font-semibold">
            {editing
              ? experience?.job_title
              : "Create professional experience"}
          </h2>

          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Manage professional history,
            responsibilities and
            presentation details.
          </p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={
            onCancel
          }
          aria-label="Close experience editor"
        >
          <X
            aria-hidden="true"
          />
        </Button>
      </div>

      <div className="space-y-6 p-5 sm:p-6">
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

        {success ? (
          <div
            role="status"
            className="flex items-start gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-4 text-sm"
          >
            <Check
              className="mt-0.5 size-4 shrink-0"
              aria-hidden="true"
            />

            {success}
          </div>
        ) : null}

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              Company name
            </span>

            <input
              value={
                form.companyName
              }
              onChange={(event) =>
                updateField(
                  "companyName",
                  event.target.value
                )
              }
              required
              minLength={2}
              maxLength={200}
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Job title
            </span>

            <input
              value={
                form.jobTitle
              }
              onChange={(event) =>
                updateField(
                  "jobTitle",
                  event.target.value
                )
              }
              required
              minLength={2}
              maxLength={200}
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium">
            Slug
          </span>

          <input
            value={
              form.slug
            }
            onChange={(event) =>
              updateSlug(
                event.target.value
              )
            }
            required
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 font-mono text-sm"
          />
        </label>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              Employment type
            </span>

            <select
              value={
                form.employmentType
              }
              onChange={(event) =>
                updateField(
                  "employmentType",
                  event.target
                    .value as EmploymentType
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            >
              <option value="full_time">
                Full-time
              </option>

              <option value="part_time">
                Part-time
              </option>

              <option value="contract">
                Contract
              </option>

              <option value="freelance">
                Freelance
              </option>

              <option value="internship">
                Internship
              </option>

              <option value="apprenticeship">
                Apprenticeship
              </option>

              <option value="temporary">
                Temporary
              </option>

              <option value="volunteer">
                Volunteer
              </option>

              <option value="self_employed">
                Self-employed
              </option>

              <option value="other">
                Other
              </option>
            </select>
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Location type
            </span>

            <select
              value={
                form.locationType
              }
              onChange={(event) =>
                updateField(
                  "locationType",
                  event.target
                    .value as ExperienceLocationType
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            >
              <option value="onsite">
                On-site
              </option>

              <option value="remote">
                Remote
              </option>

              <option value="hybrid">
                Hybrid
              </option>
            </select>
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium">
            Location
          </span>

          <input
            value={
              form.location
            }
            onChange={(event) =>
              updateField(
                "location",
                event.target.value
              )
            }
            maxLength={250}
            placeholder="Regina, Saskatchewan"
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          />
        </label>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              Start date
            </span>

            <input
              type="date"
              value={
                form.startDate
              }
              onChange={(event) =>
                updateField(
                  "startDate",
                  event.target.value
                )
              }
              required
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              End date
            </span>

            <input
              type="date"
              value={
                form.endDate
              }
              disabled={
                form.isCurrent
              }
              onChange={(event) =>
                updateField(
                  "endDate",
                  event.target.value
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-60"
            />
          </label>
        </div>

        <label className="flex w-fit cursor-pointer items-center gap-3 text-sm">
          <input
            type="checkbox"
            checked={
              form.isCurrent
            }
            onChange={(event) =>
              updateCurrent(
                event.target.checked
              )
            }
            className="size-4 rounded border-input"
          />

          This is my current position
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Summary
          </span>

          <textarea
            value={
              form.summary
            }
            onChange={(event) =>
              updateField(
                "summary",
                event.target.value
              )
            }
            required
            minLength={10}
            maxLength={10000}
            rows={5}
            className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6"
          />

          <p className="mt-1 text-right text-xs text-muted-foreground">
            {
              form.summary.length
            }
            /10000
          </p>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Responsibilities
          </span>

          <textarea
            value={
              form.responsibilities
            }
            onChange={(event) =>
              updateField(
                "responsibilities",
                event.target.value
              )
            }
            maxLength={30000}
            rows={7}
            className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6"
          />

          <p className="mt-1 text-right text-xs text-muted-foreground">
            {
              form.responsibilities.length
            }
            /30000
          </p>
        </label>

        <label className="block">
          <span className="text-sm font-medium">
            Achievements
          </span>

          <textarea
            value={
              form.achievements
            }
            onChange={(event) =>
              updateField(
                "achievements",
                event.target.value
              )
            }
            maxLength={30000}
            rows={7}
            className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6"
          />

          <p className="mt-1 text-right text-xs text-muted-foreground">
            {
              form.achievements.length
            }
            /30000
          </p>
        </label>

        <div className="grid gap-5 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              Company website
            </span>

            <input
              type="url"
              value={
                form.companyWebsite
              }
              onChange={(event) =>
                updateField(
                  "companyWebsite",
                  event.target.value
                )
              }
              maxLength={2048}
              placeholder="https://company.com"
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Company logo URL
            </span>

            <input
              type="url"
              value={
                form.companyLogoUrl
              }
              onChange={(event) =>
                updateField(
                  "companyLogoUrl",
                  event.target.value
                )
              }
              maxLength={2048}
              placeholder="https://company.com/logo.png"
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>
        </div>

        <label className="block sm:max-w-xs">
          <span className="text-sm font-medium">
            Sort order
          </span>

          <input
            type="number"
            min={0}
            step={1}
            value={
              form.sortOrder
            }
            onChange={(event) =>
              updateField(
                "sortOrder",
                event.target.value
              )
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
          />
        </label>

        {!editing ? (
          <div className="space-y-3 rounded-xl border border-border bg-muted/20 p-4">
            <p className="text-sm font-medium">
              Initial publication
            </p>

            <label className="flex w-fit cursor-pointer items-center gap-3 text-sm">
              <input
                type="checkbox"
                checked={
                  form.isPublic
                }
                onChange={(event) =>
                  updatePublic(
                    event.target.checked
                  )
                }
                className="size-4 rounded border-input"
              />

              Create as public
            </label>

            <label
              className={
                form.isPublic
                  ? "flex w-fit cursor-pointer items-center gap-3 text-sm"
                  : "flex w-fit cursor-not-allowed items-center gap-3 text-sm text-muted-foreground"
              }
            >
              <input
                type="checkbox"
                checked={
                  form.isFeatured
                }
                disabled={
                  !form.isPublic
                }
                onChange={(event) =>
                  updateField(
                    "isFeatured",
                    event.target.checked
                  )
                }
                className="size-4 rounded border-input"
              />

              Create as featured
            </label>
          </div>
        ) : (
          <p className="text-xs leading-5 text-muted-foreground">
            Public and featured states are
            managed separately from
            experience content.
          </p>
        )}
      </div>

      <div className="flex flex-wrap justify-end gap-2 border-t border-border p-4 sm:p-5">
        <Button
          type="button"
          variant="outline"
          disabled={
            saving
          }
          onClick={
            onCancel
          }
        >
          Cancel
        </Button>

        <Button
          type="submit"
          disabled={
            saving
          }
        >
          {saving ? (
            <Loader2
              className="animate-spin"
              aria-hidden="true"
            />
          ) : (
            <Save
              aria-hidden="true"
            />
          )}

          {saving
            ? "Saving..."
            : editing
              ? "Save changes"
              : "Create experience"}
        </Button>
      </div>
    </form>
  )
}