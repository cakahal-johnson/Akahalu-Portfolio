"use client"

import {
  AlertCircle,
  Check,
  Loader2,
  Save,
  Search,
} from "lucide-react"
import {
  useEffect,
  useMemo,
  useState,
  type FormEvent,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminProjectService,
} from "@/services/admin"

import {
  publicPortfolioService,
} from "@/services/portfolio"

import type {
  ProjectCategoryRead,
  ProjectTechnologyRead,
} from "@/types/portfolio"

import type {
  ProjectAdminRead,
  ProjectUpdate,
} from "@/types/portfolio/project"

type AdminProjectEditorProps = {
  project:
    ProjectAdminRead

  onProjectChange: (
    project:
      ProjectAdminRead
  ) => void
}

type ProjectFormState = {
  title: string
  slug: string

  shortDescription: string
  description: string

  problemStatement: string
  solutionSummary: string
  keyFeatures: string
  technicalHighlights: string

  categoryId: string

  repositoryUrl: string
  liveUrl: string
  caseStudyUrl: string
  thumbnailUrl: string

  startedAt: string
  completedAt: string

  sortOrder: string

  seoTitle: string
  seoDescription: string
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

function isoToLocalDateTime(
  value:
    string | null
): string {
  if (
    !value
  ) {
    return ""
  }

  const date =
    new Date(
      value
    )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return ""
  }

  const localDate =
    new Date(
      date.getTime() -
        date.getTimezoneOffset() *
          60_000
    )

  return localDate
    .toISOString()
    .slice(
      0,
      16
    )
}

function localDateTimeToIso(
  value:
    string
): string | null {
  if (
    !value.trim()
  ) {
    return null
  }

  const date =
    new Date(
      value
    )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return null
  }

  return date.toISOString()
}

function projectToForm(
  project:
    ProjectAdminRead
): ProjectFormState {
  return {
    title:
      project.title,

    slug:
      project.slug,

    shortDescription:
      project.short_description,

    description:
      project.description,

    problemStatement:
      project.problem_statement ??
      "",

    solutionSummary:
      project.solution_summary ??
      "",

    keyFeatures:
      project.key_features ??
      "",

    technicalHighlights:
      project.technical_highlights ??
      "",

    categoryId:
      project.category_id ??
      "",

    repositoryUrl:
      project.repository_url ??
      "",

    liveUrl:
      project.live_url ??
      "",

    caseStudyUrl:
      project.case_study_url ??
      "",

    thumbnailUrl:
      project.thumbnail_url ??
      "",

    startedAt:
      isoToLocalDateTime(
        project.started_at
      ),

    completedAt:
      isoToLocalDateTime(
        project.completed_at
      ),

    sortOrder:
      String(
        project.sort_order
      ),

    seoTitle:
      project.seo_title ??
      "",

    seoDescription:
      project.seo_description ??
      "",
  }
}

type TextFieldProps = {
  label: string
  value: string

  onChange: (
    value:
      string
  ) => void

  type?: string
  required?: boolean

  minLength?: number
  maxLength?: number

  min?: number
  step?: number

  placeholder?: string
  helperText?: string

  disabled?: boolean
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  minLength,
  maxLength,
  min,
  step,
  placeholder,
  helperText,
  disabled = false,
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium">
        {label}
      </span>

      <input
        type={type}
        value={
          value
        }
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        required={
          required
        }
        minLength={
          minLength
        }
        maxLength={
          maxLength
        }
        min={
          min
        }
        step={
          step
        }
        placeholder={
          placeholder
        }
        disabled={
          disabled
        }
        className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
      />

      {helperText ? (
        <p className="mt-1.5 text-xs leading-5 text-muted-foreground">
          {helperText}
        </p>
      ) : null}
    </label>
  )
}

type TextAreaFieldProps = {
  label: string
  value: string

  onChange: (
    value:
      string
  ) => void

  required?: boolean

  minLength?: number
  maxLength?: number

  rows?: number
  helperText?: string

  disabled?: boolean
}

function TextAreaField({
  label,
  value,
  onChange,
  required = false,
  minLength,
  maxLength,
  rows = 6,
  helperText,
  disabled = false,
}: TextAreaFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium">
        {label}
      </span>

      <textarea
        value={
          value
        }
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        required={
          required
        }
        minLength={
          minLength
        }
        maxLength={
          maxLength
        }
        rows={
          rows
        }
        disabled={
          disabled
        }
        className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6 outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:opacity-50"
      />

      <div className="mt-1.5 flex justify-between gap-4 text-xs text-muted-foreground">
        {helperText ? (
          <span>
            {helperText}
          </span>
        ) : (
          <span />
        )}

        {maxLength ? (
          <span className="shrink-0">
            {value.length}/
            {maxLength}
          </span>
        ) : null}
      </div>
    </label>
  )
}

export function AdminProjectEditor({
  project,
  onProjectChange,
}: AdminProjectEditorProps) {
  const [
    form,
    setForm,
  ] =
    useState<ProjectFormState>(
      () =>
        projectToForm(
          project
        )
    )

  const [
    categories,
    setCategories,
  ] =
    useState<ProjectCategoryRead[]>(
      []
    )

  const [
    technologies,
    setTechnologies,
  ] =
    useState<ProjectTechnologyRead[]>(
      []
    )

  const [
    selectedTechnologyIds,
    setSelectedTechnologyIds,
  ] =
    useState<string[]>(
      () =>
        project.technology_assignments.map(
          (
            assignment
          ) =>
            assignment
              .technology
              .id
        )
    )

  const [
    technologySearch,
    setTechnologySearch,
  ] =
    useState("")

  const [
    optionsLoading,
    setOptionsLoading,
  ] =
    useState(true)

  const [
    optionsError,
    setOptionsError,
  ] =
    useState<string | null>(
      null
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

  const deleted =
    project.deleted_at !==
    null


  useEffect(() => {
    let cancelled =
      false

    async function loadOptions() {
      const [
        categoryResult,
        technologyResult,
      ] =
        await Promise.allSettled(
          [
            publicPortfolioService.getCategories(),
            publicPortfolioService.getTechnologies(),
          ]
        )

      if (
        cancelled
      ) {
        return
      }

      if (
        categoryResult.status ===
        "fulfilled"
      ) {
        setCategories(
          categoryResult.value
        )
      }

      if (
        technologyResult.status ===
        "fulfilled"
      ) {
        setTechnologies(
          technologyResult.value
        )
      }

      if (
        categoryResult.status ===
          "rejected" ||
        technologyResult.status ===
          "rejected"
      ) {
        setOptionsError(
          "Some project classification options could not be loaded."
        )
      }

      setOptionsLoading(
        false
      )
    }

    void loadOptions()

    return () => {
      cancelled =
        true
    }
  }, [])

  const filteredTechnologies =
    useMemo(
      () => {
        const search =
          technologySearch
            .trim()
            .toLowerCase()

        if (
          !search
        ) {
          return technologies
        }

        return technologies.filter(
          (
            technology
          ) =>
            technology.name
              .toLowerCase()
              .includes(
                search
              ) ||
            technology.category
              .toLowerCase()
              .includes(
                search
              )
        )
      },
      [
        technologies,
        technologySearch,
      ]
    )

  function updateField<
    TKey extends keyof ProjectFormState,
  >(
    key:
      TKey,
    value:
      ProjectFormState[TKey]
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

  function toggleTechnology(
    technologyId:
      string
  ) {
    setSelectedTechnologyIds(
      (
        current
      ) => {
        if (
          current.includes(
            technologyId
          )
        ) {
          return current.filter(
            (
              id
            ) =>
              id !==
              technologyId
          )
        }

        return [
          ...current,
          technologyId,
        ]
      }
    )

    setError(
      null
    )

    setSuccess(
      null
    )
  }

  function buildPayload():
    | ProjectUpdate
    | null {
    const title =
      form.title.trim()

    const slug =
      slugify(
        form.slug
      )

    const shortDescription =
      form.shortDescription.trim()

    const description =
      form.description.trim()

    if (
      title.length <
      2
    ) {
      setError(
        "Project title must contain at least 2 characters."
      )

      return null
    }

    if (
      !slug
    ) {
      setError(
        "A project slug is required."
      )

      return null
    }

    if (
      shortDescription.length <
      10
    ) {
      setError(
        "Short description must contain at least 10 characters."
      )

      return null
    }

    if (
      description.length <
      20
    ) {
      setError(
        "Project description must contain at least 20 characters."
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

    const startedAt =
      localDateTimeToIso(
        form.startedAt
      )

    const completedAt =
      localDateTimeToIso(
        form.completedAt
      )

    if (
      form.startedAt &&
      !startedAt
    ) {
      setError(
        "Project start date is invalid."
      )

      return null
    }

    if (
      form.completedAt &&
      !completedAt
    ) {
      setError(
        "Project completion date is invalid."
      )

      return null
    }

    if (
      startedAt &&
      completedAt &&
      new Date(
        completedAt
      ).getTime() <
        new Date(
          startedAt
        ).getTime()
    ) {
      setError(
        "Project completion date cannot be before its start date."
      )

      return null
    }

    return {
      title,
      slug,

      short_description:
        shortDescription,

      description,

      problem_statement:
        nullable(
          form.problemStatement
        ),

      solution_summary:
        nullable(
          form.solutionSummary
        ),

      key_features:
        nullable(
          form.keyFeatures
        ),

      technical_highlights:
        nullable(
          form.technicalHighlights
        ),

      category_id:
        form.categoryId ||
        null,

      sort_order:
        sortOrder,

      repository_url:
        nullable(
          form.repositoryUrl
        ),

      live_url:
        nullable(
          form.liveUrl
        ),

      case_study_url:
        nullable(
          form.caseStudyUrl
        ),

      thumbnail_url:
        nullable(
          form.thumbnailUrl
        ),

      started_at:
        startedAt,

      completed_at:
        completedAt,

      seo_title:
        nullable(
          form.seoTitle
        ),

      seo_description:
        nullable(
          form.seoDescription
        ),

      technology_assignments:
        selectedTechnologyIds.map(
          (
            technologyId,
            index
          ) => {
            const existing =
              project.technology_assignments.find(
                (
                  assignment
                ) =>
                  assignment
                    .technology
                    .id ===
                  technologyId
              )

            return {
              technology_id:
                technologyId,

              is_featured:
                existing
                  ?.is_featured ??
                false,

              sort_order:
                index,
            }
          }
        ),
    }
  }

  async function saveProject(
    event:
      FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (
      saving ||
      deleted
    ) {
      return
    }

    const payload =
      buildPayload()

    if (
      !payload
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

                 const updated =
        await adminProjectService.updateProject(
          project.id,
          payload
        )

      /*
       * Apply the canonical values returned
       * by FastAPI only after a successful
       * content save.
       *
       * Lifecycle-only parent updates must
       * not reset unsaved editor state.
       */
      setForm(
        projectToForm(
          updated
        )
      )

      setSelectedTechnologyIds(
        updated.technology_assignments.map(
          (
            assignment
          ) =>
            assignment
              .technology
              .id
        )
      )

      onProjectChange(
        updated
      )

      setSuccess(
        "Project changes saved successfully."
      )
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The project could not be updated."
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
        saveProject
      }
      className="space-y-6"
    >
      {deleted ? (
        <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          This project is deleted.
          Restore it before editing
          project content.
        </div>
      ) : null}

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

      {optionsError ? (
        <div className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm">
          <AlertCircle
            className="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />

          {optionsError}
        </div>
      ) : null}

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Project identity
        </h2>

        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          Edit the project title, URL slug
          and portfolio description.
        </p>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="Project title"
            value={
              form.title
            }
            onChange={(value) =>
              updateField(
                "title",
                value
              )
            }
            required
            minLength={2}
            maxLength={200}
            disabled={
              deleted
            }
          />

          <TextField
            label="Slug"
            value={
              form.slug
            }
            onChange={
              updateSlug
            }
            required
            disabled={
              deleted
            }
          />
        </div>

        <div className="mt-5">
          <TextAreaField
            label="Short description"
            value={
              form.shortDescription
            }
            onChange={(value) =>
              updateField(
                "shortDescription",
                value
              )
            }
            required
            minLength={10}
            maxLength={500}
            rows={4}
            disabled={
              deleted
            }
          />
        </div>

        <div className="mt-5">
          <TextAreaField
            label="Full description"
            value={
              form.description
            }
            onChange={(value) =>
              updateField(
                "description",
                value
              )
            }
            required
            minLength={20}
            maxLength={50000}
            rows={10}
            disabled={
              deleted
            }
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Case study
        </h2>

        <div className="mt-5 grid gap-5 xl:grid-cols-2">
          <TextAreaField
            label="Problem statement"
            value={
              form.problemStatement
            }
            onChange={(value) =>
              updateField(
                "problemStatement",
                value
              )
            }
            maxLength={20000}
            rows={7}
            disabled={
              deleted
            }
          />

          <TextAreaField
            label="Solution summary"
            value={
              form.solutionSummary
            }
            onChange={(value) =>
              updateField(
                "solutionSummary",
                value
              )
            }
            maxLength={20000}
            rows={7}
            disabled={
              deleted
            }
          />

          <TextAreaField
            label="Key features"
            value={
              form.keyFeatures
            }
            onChange={(value) =>
              updateField(
                "keyFeatures",
                value
              )
            }
            maxLength={30000}
            rows={7}
            disabled={
              deleted
            }
          />

          <TextAreaField
            label="Technical highlights"
            value={
              form.technicalHighlights
            }
            onChange={(value) =>
              updateField(
                "technicalHighlights",
                value
              )
            }
            maxLength={30000}
            rows={7}
            disabled={
              deleted
            }
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Classification
        </h2>

        <p className="mt-1 text-sm leading-6 text-muted-foreground">
          Manage the category and
          technologies assigned to this
          project.
        </p>

        {optionsLoading ? (
          <div className="mt-5 flex min-h-32 items-center justify-center rounded-xl border border-border">
            <Loader2
              className="size-5 animate-spin text-muted-foreground"
              aria-hidden="true"
            />
          </div>
        ) : (
          <>
            <label className="mt-5 block">
              <span className="text-sm font-medium">
                Category
              </span>

              <select
                value={
                  form.categoryId
                }
                disabled={
                  deleted
                }
                onChange={(event) =>
                  updateField(
                    "categoryId",
                    event.target.value
                  )
                }
                className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="">
                  No category
                </option>

                {categories.map(
                  (
                    category
                  ) => (
                    <option
                      key={
                        category.id
                      }
                      value={
                        category.id
                      }
                    >
                      {
                        category.name
                      }
                    </option>
                  )
                )}
              </select>

              <p className="mt-1.5 text-xs text-muted-foreground">
                A category is required
                before publishing.
              </p>
            </label>

            <div className="mt-6">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <span className="text-sm font-medium">
                    Technologies
                  </span>

                  <p className="mt-1 text-xs text-muted-foreground">
                    {
                      selectedTechnologyIds.length
                    } selected
                  </p>
                </div>

                <label className="relative block w-full sm:max-w-xs">
                  <span className="sr-only">
                    Search technologies
                  </span>

                  <Search
                    className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
                    aria-hidden="true"
                  />

                  <input
                    type="search"
                    value={
                      technologySearch
                    }
                    disabled={
                      deleted
                    }
                    onChange={(event) =>
                      setTechnologySearch(
                        event.target.value
                      )
                    }
                    placeholder="Search technologies"
                    className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </label>
              </div>

              <div className="mt-4 max-h-96 overflow-y-auto rounded-xl border border-border">
                {filteredTechnologies.length >
                0 ? (
                  <div className="grid gap-px bg-border sm:grid-cols-2 xl:grid-cols-3">
                    {filteredTechnologies.map(
                      (
                        technology
                      ) => {
                        const selected =
                          selectedTechnologyIds.includes(
                            technology.id
                          )

                        return (
                          <button
                            key={
                              technology.id
                            }
                            type="button"
                            disabled={
                              deleted
                            }
                            onClick={() =>
                              toggleTechnology(
                                technology.id
                              )
                            }
                            aria-pressed={
                              selected
                            }
                            className="flex min-h-20 items-start gap-3 bg-background p-4 text-left transition-colors hover:bg-muted/50 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            <span
                              className={
                                selected
                                  ? "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded border border-primary bg-primary text-primary-foreground"
                                  : "mt-0.5 flex size-5 shrink-0 items-center justify-center rounded border border-input"
                              }
                            >
                              {selected ? (
                                <Check
                                  className="size-3.5"
                                  aria-hidden="true"
                                />
                              ) : null}
                            </span>

                            <span className="min-w-0">
                              <span className="block font-medium">
                                {
                                  technology.name
                                }
                              </span>

                              <span className="mt-1 block text-xs capitalize text-muted-foreground">
                                {
                                  technology.category
                                }
                              </span>
                            </span>
                          </button>
                        )
                      }
                    )}
                  </div>
                ) : (
                  <div className="p-8 text-center text-sm text-muted-foreground">
                    No technologies match
                    your search.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Links & media
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="Repository URL"
            type="url"
            value={
              form.repositoryUrl
            }
            onChange={(value) =>
              updateField(
                "repositoryUrl",
                value
              )
            }
            disabled={
              deleted
            }
          />

          <TextField
            label="Live URL"
            type="url"
            value={
              form.liveUrl
            }
            onChange={(value) =>
              updateField(
                "liveUrl",
                value
              )
            }
            disabled={
              deleted
            }
          />

          <TextField
            label="Case study URL"
            type="url"
            value={
              form.caseStudyUrl
            }
            onChange={(value) =>
              updateField(
                "caseStudyUrl",
                value
              )
            }
            disabled={
              deleted
            }
          />

          <TextField
            label="Thumbnail URL"
            type="url"
            value={
              form.thumbnailUrl
            }
            onChange={(value) =>
              updateField(
                "thumbnailUrl",
                value
              )
            }
            disabled={
              deleted
            }
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Timeline & ordering
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <TextField
            label="Started at"
            type="datetime-local"
            value={
              form.startedAt
            }
            onChange={(value) =>
              updateField(
                "startedAt",
                value
              )
            }
            disabled={
              deleted
            }
          />

          <TextField
            label="Completed at"
            type="datetime-local"
            value={
              form.completedAt
            }
            onChange={(value) =>
              updateField(
                "completedAt",
                value
              )
            }
            disabled={
              deleted
            }
          />

          <TextField
            label="Sort order"
            type="number"
            value={
              form.sortOrder
            }
            onChange={(value) =>
              updateField(
                "sortOrder",
                value
              )
            }
            min={0}
            step={1}
            disabled={
              deleted
            }
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Search metadata
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="SEO title"
            value={
              form.seoTitle
            }
            onChange={(value) =>
              updateField(
                "seoTitle",
                value
              )
            }
            maxLength={70}
            disabled={
              deleted
            }
          />

          <TextField
            label="SEO description"
            value={
              form.seoDescription
            }
            onChange={(value) =>
              updateField(
                "seoDescription",
                value
              )
            }
            maxLength={170}
            disabled={
              deleted
            }
          />
        </div>
      </section>

      {!deleted ? (
        <div className="sticky bottom-4 z-20 flex justify-end">
          <div className="rounded-xl border border-border bg-background/95 p-2 shadow-lg backdrop-blur">
            <Button
              type="submit"
              size="lg"
              disabled={
                saving
              }
            >
              {saving ? (
                <>
                  <Loader2
                    className="animate-spin"
                    aria-hidden="true"
                  />

                  Saving...
                </>
              ) : (
                <>
                  <Save
                    aria-hidden="true"
                  />

                  Save changes
                </>
              )}
            </Button>
          </div>
        </div>
      ) : null}
    </form>
  )
}