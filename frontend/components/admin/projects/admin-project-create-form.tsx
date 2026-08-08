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
  useRouter,
} from "next/navigation"

import { Button } from "@/components/ui/button"

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
  ProjectCreate,
} from "@/types/portfolio/project"

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

const emptyForm: ProjectFormState = {
  title: "",
  slug: "",

  shortDescription: "",
  description: "",

  problemStatement: "",
  solutionSummary: "",
  keyFeatures: "",
  technicalHighlights: "",

  categoryId: "",

  repositoryUrl: "",
  liveUrl: "",
  caseStudyUrl: "",
  thumbnailUrl: "",

  startedAt: "",
  completedAt: "",

  sortOrder: "0",

  seoTitle: "",
  seoDescription: "",
}

function nullable(
  value: string
): string | null {
  const normalized =
    value.trim()

  return normalized
    ? normalized
    : null
}

function slugify(
  value: string
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

function dateTimeToIso(
  value: string
): string | null {
  if (!value.trim()) {
    return null
  }

  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return null
  }

  return date.toISOString()
}

type TextFieldProps = {
  label: string
  value: string
  onChange: (
    value: string
  ) => void

  type?: string
  required?: boolean

  minLength?: number
  maxLength?: number

  min?: number
  step?: number

  placeholder?: string

  helperText?: string
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
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium">
        {label}
      </span>

      <input
        type={type}
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        required={required}
        minLength={minLength}
        maxLength={maxLength}
        min={min}
        step={step}
        placeholder={placeholder}
        className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
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
    value: string
  ) => void

  required?: boolean

  minLength?: number
  maxLength?: number

  rows?: number

  helperText?: string
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
}: TextAreaFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium">
        {label}
      </span>

      <textarea
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        required={required}
        minLength={minLength}
        maxLength={maxLength}
        rows={rows}
        className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6 outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
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
            {value.length}/{maxLength}
          </span>
        ) : null}
      </div>
    </label>
  )
}

export function AdminProjectCreateForm() {
  const router =
    useRouter()

  const [
    form,
    setForm,
  ] =
    useState<ProjectFormState>(
      emptyForm
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
      []
    )

  const [
    technologySearch,
    setTechnologySearch,
  ] =
    useState("")

  const [
    slugEdited,
    setSlugEdited,
  ] =
    useState(false)

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

      if (cancelled) {
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
          "Some project classification options could not be loaded. You can still create the project and assign them later."
        )
      }

      setOptionsLoading(
        false
      )
    }

    void loadOptions()

    return () => {
      cancelled = true
    }
  }, [])

  const filteredTechnologies =
    useMemo(
      () => {
        const search =
          technologySearch
            .trim()
            .toLowerCase()

        if (!search) {
          return technologies
        }

        return technologies.filter(
          (technology) =>
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
    key: TKey,
    value: ProjectFormState[TKey]
  ) {
    setForm(
      (current) => ({
        ...current,
        [key]:
          value,
      })
    )

    setError(
      null
    )
  }

  function updateTitle(
    value: string
  ) {
    setForm(
      (current) => ({
        ...current,

        title:
          value,

        slug:
          slugEdited
            ? current.slug
            : slugify(
                value
              ),
      })
    )

    setError(
      null
    )
  }

  function updateSlug(
    value: string
  ) {
    setSlugEdited(
      true
    )

    setForm(
      (current) => ({
        ...current,

        slug:
          slugify(
            value
          ),
      })
    )

    setError(
      null
    )
  }

  function toggleTechnology(
    technologyId: string
  ) {
    setSelectedTechnologyIds(
      (current) => {
        if (
          current.includes(
            technologyId
          )
        ) {
          return current.filter(
            (id) =>
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
  }

  function buildPayload():
    | ProjectCreate
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
      title.length < 2
    ) {
      setError(
        "Project title must contain at least 2 characters."
      )

      return null
    }

    if (!slug) {
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
      sortOrder < 0
    ) {
      setError(
        "Sort order must be a whole number of 0 or greater."
      )

      return null
    }

    const startedAt =
      dateTimeToIso(
        form.startedAt
      )

    const completedAt =
      dateTimeToIso(
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

      status:
        "draft",

      visibility:
        "private",

      is_featured:
        false,

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

      published_at:
        null,

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
          ) => ({
            technology_id:
              technologyId,

            is_featured:
              false,

            sort_order:
              index,
          })
        ),
    }
  }

  async function createProject(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (saving) {
      return
    }

    const payload =
      buildPayload()

    if (!payload) {
      return
    }

    try {
      setSaving(
        true
      )

      setError(
        null
      )

      await adminProjectService.createProject(
        payload
      )

      router.push(
        "/admin/projects"
      )

      router.refresh()
    } catch (caughtError) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The project could not be created."
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
        createProject
      }
      className="space-y-6"
    >
      <section className="rounded-2xl border border-primary/20 bg-primary/5 p-5 sm:p-6">
        <h2 className="font-semibold">
          Draft project
        </h2>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          New projects are created as
          private drafts. Publishing,
          visibility, featured state,
          links and media can be managed
          through the dedicated project
          management steps afterward.
        </p>
      </section>

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

      {optionsError ? (
        <div
          role="status"
          className="flex items-start gap-3 rounded-xl border border-amber-500/30 bg-amber-500/5 p-4 text-sm"
        >
          <AlertCircle
            className="mt-0.5 size-4 shrink-0"
            aria-hidden="true"
          />

          {optionsError}
        </div>
      ) : null}

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div>
          <h2 className="text-lg font-semibold">
            Project identity
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Define the project name,
            permanent URL slug and summary.
          </p>
        </div>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="Project title"
            value={
              form.title
            }
            onChange={
              updateTitle
            }
            required
            minLength={2}
            maxLength={200}
            placeholder="Akahalu Portfolio"
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
            placeholder="akahalu-portfolio"
            helperText="Generated from the title until you edit it manually."
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
            helperText="Used in project cards, summaries and portfolio listings."
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
            helperText="Describe the project, its scope, implementation and outcome."
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div>
          <h2 className="text-lg font-semibold">
            Case study
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Capture the problem, solution,
            important functionality and
            technical decisions.
          </p>
        </div>

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
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div>
          <h2 className="text-lg font-semibold">
            Classification
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Assign an optional project
            category and the technologies
            used to build it.
          </p>
        </div>

        {optionsLoading ? (
          <div className="mt-5 flex min-h-32 items-center justify-center rounded-xl border border-border">
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <Loader2
                className="size-4 animate-spin"
                aria-hidden="true"
              />

              Loading categories and
              technologies...
            </div>
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
                onChange={(event) =>
                  updateField(
                    "categoryId",
                    event.target.value
                  )
                }
                className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              >
                <option value="">
                  No category yet
                </option>

                {categories.map(
                  (category) => (
                    <option
                      key={
                        category.id
                      }
                      value={
                        category.id
                      }
                    >
                      {category.name}
                    </option>
                  )
                )}
              </select>

              <p className="mt-1.5 text-xs text-muted-foreground">
                A category becomes
                mandatory before the
                project can be published.
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
                    onChange={(event) =>
                      setTechnologySearch(
                        event.target.value
                      )
                    }
                    placeholder="Search technologies"
                    className="h-10 w-full rounded-lg border border-input bg-background pl-9 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
                  />
                </label>
              </div>

              <div className="mt-4 max-h-96 overflow-y-auto rounded-xl border border-border">
                {filteredTechnologies.length >
                0 ? (
                  <div className="grid gap-px bg-border sm:grid-cols-2 xl:grid-cols-3">
                    {filteredTechnologies.map(
                      (technology) => {
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
                            onClick={() =>
                              toggleTechnology(
                                technology.id
                              )
                            }
                            className="flex min-h-20 items-start gap-3 bg-background p-4 text-left transition-colors hover:bg-muted/50"
                            aria-pressed={
                              selected
                            }
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
        <div>
          <h2 className="text-lg font-semibold">
            Links & media
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Add primary project URLs.
            Dedicated project links and
            media galleries will be
            managed separately.
          </p>
        </div>

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
            placeholder="https://github.com/..."
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
            placeholder="https://..."
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
            placeholder="https://..."
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
            placeholder="https://..."
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div>
          <h2 className="text-lg font-semibold">
            Timeline & ordering
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Record the project timeline
            and its preferred portfolio
            ordering.
          </p>
        </div>

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
            helperText="Lower values appear earlier when display order is used."
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div>
          <h2 className="text-lg font-semibold">
            Search metadata
          </h2>

          <p className="mt-1 text-sm leading-6 text-muted-foreground">
            Prepare optional metadata for
            search engines and social
            previews.
          </p>
        </div>

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
          />
        </div>
      </section>

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

                Creating...
              </>
            ) : (
              <>
                <Save
                  aria-hidden="true"
                />

                Create draft
              </>
            )}
          </Button>
        </div>
      </div>
    </form>
  )
}