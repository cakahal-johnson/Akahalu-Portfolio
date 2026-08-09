"use client"

import {
  AlertCircle,
  BriefcaseBusiness,
  Loader2,
  Plus,
} from "lucide-react"

import {
  useEffect,
  useState,
} from "react"

import {
  AdminExperienceCard,
} from "@/components/admin/experiences/admin-experience-card"

import {
  AdminExperienceFilters,
} from "@/components/admin/experiences/admin-experience-filters"

import {
  AdminExperienceForm,
} from "@/components/admin/experiences/admin-experience-form"

import type {
  ExperienceBusyAction,
} from "@/components/admin/experiences/admin-experience-lifecycle"

import {
  defaultExperienceAdminFilters,
  type ExperienceAdminFilterState,
  type ExperienceBooleanFilter,
} from "@/components/admin/experiences/experience-admin-filters"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminExperienceService,
} from "@/services/admin"

import type {
  AdminExperienceListResponse,
  ExperienceAdminRead,
} from "@/types/portfolio/experience"

const PAGE_SIZE =
  10

const SEARCH_DEBOUNCE_MS =
  750

type EditorState =
  | {
      mode:
        "create"

      experience:
        null
    }
  | {
      mode:
        "edit"

      experience:
        ExperienceAdminRead
    }
  | null

function booleanFilterValue(
  value:
    ExperienceBooleanFilter
): boolean | undefined {
  if (
    value ===
    "yes"
  ) {
    return true
  }

  if (
    value ===
    "no"
  ) {
    return false
  }

  return undefined
}

export function AdminExperienceManager() {
  const [
    experiences,
    setExperiences,
  ] =
    useState<AdminExperienceListResponse | null>(
      null
    )

  const [
    filters,
    setFilters,
  ] =
    useState<ExperienceAdminFilterState>(
      defaultExperienceAdminFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      defaultExperienceAdminFilters.search
    )

  const [
    page,
    setPage,
  ] =
    useState(1)

  const [
    reloadVersion,
    setReloadVersion,
  ] =
    useState(0)

  const [
    loading,
    setLoading,
  ] =
    useState(true)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  const [
    editor,
    setEditor,
  ] =
    useState<EditorState>(
      null
    )

  const [
    busyExperience,
    setBusyExperience,
  ] =
    useState<{
      id: string

      action:
        ExperienceBusyAction
    } | null>(
      null
    )

  const {
    search:
      filterSearch,

    employmentType:
      filterEmploymentType,

    locationType:
      filterLocationType,

    current:
      filterCurrent,

    visibility:
      filterVisibility,

    featured:
      filterFeatured,

    includeDeleted:
      filterIncludeDeleted,

    sortBy:
      filterSortBy,

    sortDirection:
      filterSortDirection,
  } =
    filters

  useEffect(() => {
    if (
      filterSearch ===
      debouncedSearch
    ) {
      return
    }

    const timeoutId =
      window.setTimeout(
        () => {
          setLoading(
            true
          )

          setError(
            null
          )

          setPage(
            1
          )

          setDebouncedSearch(
            filterSearch
          )
        },
        SEARCH_DEBOUNCE_MS
      )

    return () => {
      window.clearTimeout(
        timeoutId
      )
    }
  }, [
    filterSearch,
    debouncedSearch,
  ])

  useEffect(() => {
    let cancelled =
      false

    const request =
      adminExperienceService.getExperiences(
        {
          page,

          page_size:
            PAGE_SIZE,

          search:
            debouncedSearch.trim() ||
            undefined,

          employment_type:
            filterEmploymentType ===
            "all"
              ? undefined
              : filterEmploymentType,

          location_type:
            filterLocationType ===
            "all"
              ? undefined
              : filterLocationType,

          is_current:
            booleanFilterValue(
              filterCurrent
            ),

          is_public:
            booleanFilterValue(
              filterVisibility
            ),

          is_featured:
            booleanFilterValue(
              filterFeatured
            ),

          include_deleted:
            filterIncludeDeleted,

          sort_by:
            filterSortBy,

          sort_direction:
            filterSortDirection,
        }
      )

    void request
      .then(
        (result) => {
          if (
            cancelled
          ) {
            return
          }

          setExperiences(
            result
          )

          setError(
            null
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (
            cancelled
          ) {
            return
          }

          setError(
            caughtError instanceof
            AdminApiError
              ? caughtError.message
              : "Experiences could not be loaded."
          )
        }
      )
      .finally(
        () => {
          if (
            cancelled
          ) {
            return
          }

          setLoading(
            false
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    page,
    debouncedSearch,
    filterEmploymentType,
    filterLocationType,
    filterCurrent,
    filterVisibility,
    filterFeatured,
    filterIncludeDeleted,
    filterSortBy,
    filterSortDirection,
    reloadVersion,
  ])

  function beginReload() {
    setLoading(
      true
    )

    setError(
      null
    )
  }

  function reloadExperiences() {
    beginReload()

    setReloadVersion(
      (
        current
      ) =>
        current + 1
    )
  }

  function changeFilters(
    nextFilters:
      ExperienceAdminFilterState
  ) {
    const searchChanged =
      nextFilters.search !==
      filters.search

    const nonSearchChanged =
      nextFilters.employmentType !==
        filters.employmentType ||
      nextFilters.locationType !==
        filters.locationType ||
      nextFilters.current !==
        filters.current ||
      nextFilters.visibility !==
        filters.visibility ||
      nextFilters.featured !==
        filters.featured ||
      nextFilters.includeDeleted !==
        filters.includeDeleted ||
      nextFilters.sortBy !==
        filters.sortBy ||
      nextFilters.sortDirection !==
        filters.sortDirection

    if (
      nonSearchChanged
    ) {
      beginReload()

      setDebouncedSearch(
        nextFilters.search
      )

      setPage(
        1
      )
    }

    setFilters(
      nextFilters
    )

    if (
      searchChanged &&
      !nonSearchChanged
    ) {
      return
    }
  }

  function resetFilters() {
    reloadExperiences()

    setFilters(
      defaultExperienceAdminFilters
    )

    setDebouncedSearch(
      defaultExperienceAdminFilters.search
    )

    setPage(
      1
    )
  }

  function changePage(
    nextPage:
      number
  ) {
    if (
      nextPage ===
      page
    ) {
      return
    }

    beginReload()

    setPage(
      nextPage
    )
  }

  function openCreate() {
    setError(
      null
    )

    setEditor({
      mode:
        "create",

      experience:
        null,
    })
  }

  function openEdit(
    experience:
      ExperienceAdminRead
  ) {
    setError(
      null
    )

    setEditor({
      mode:
        "edit",

      experience,
    })
  }

  function closeEditor() {
    setEditor(
      null
    )
  }

  function updateEditor(
    experience:
      ExperienceAdminRead
  ) {
    if (
      editor?.mode ===
        "edit" &&
      editor.experience.id ===
        experience.id
    ) {
      setEditor({
        mode:
          "edit",

        experience,
      })
    }
  }

  function handleSaved(
    experience:
      ExperienceAdminRead,
    created:
      boolean
  ) {
    setEditor({
      mode:
        "edit",

      experience,
    })

    if (
      created
    ) {
      setPage(
        1
      )
    }

    reloadExperiences()
  }

  async function toggleVisibility(
    experience:
      ExperienceAdminRead
  ) {
    if (
      busyExperience ||
      experience.deleted_at
    ) {
      return
    }

    try {
      setBusyExperience({
        id:
          experience.id,

        action:
          "visibility",
      })

      setError(
        null
      )

      const updated =
        await adminExperienceService.updateVisibility(
          experience.id,
          {
            is_public:
              !experience.is_public,

            reason:
              experience.is_public
                ? "Experience hidden from public portfolio administration."
                : "Experience approved for public portfolio display.",
          }
        )

      updateEditor(
        updated
      )

      reloadExperiences()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Experience visibility could not be updated."
      )
    } finally {
      setBusyExperience(
        null
      )
    }
  }

  async function toggleFeatured(
    experience:
      ExperienceAdminRead
  ) {
    if (
      busyExperience ||
      experience.deleted_at ||
      !experience.is_public
    ) {
      return
    }

    try {
      setBusyExperience({
        id:
          experience.id,

        action:
          "featured",
      })

      setError(
        null
      )

      const updated =
        await adminExperienceService.updateFeatured(
          experience.id,
          {
            is_featured:
              !experience.is_featured,

            reason:
              experience.is_featured
                ? "Experience removed from portfolio highlights."
                : "Experience selected for portfolio highlights.",
          }
        )

      updateEditor(
        updated
      )

      reloadExperiences()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Experience featured status could not be updated."
      )
    } finally {
      setBusyExperience(
        null
      )
    }
  }

  async function deleteExperience(
    experience:
      ExperienceAdminRead
  ) {
    if (
      busyExperience ||
      experience.deleted_at
    ) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${experience.job_title}" at "${experience.company_name}"?\n\nThe experience will be hidden from the public portfolio and can be restored later.`
      )

    if (
      !confirmed
    ) {
      return
    }

    try {
      setBusyExperience({
        id:
          experience.id,

        action:
          "delete",
      })

      setError(
        null
      )

      await adminExperienceService.deleteExperience(
        experience.id,
        {
          reason:
            "Experience deleted from portfolio administration.",
        }
      )

      if (
        editor?.mode ===
          "edit" &&
        editor.experience.id ===
          experience.id
      ) {
        setEditor(
          null
        )
      }

      reloadExperiences()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The experience could not be deleted."
      )
    } finally {
      setBusyExperience(
        null
      )
    }
  }

  async function restoreExperience(
    experience:
      ExperienceAdminRead
  ) {
    if (
      busyExperience ||
      !experience.deleted_at
    ) {
      return
    }

    try {
      setBusyExperience({
        id:
          experience.id,

        action:
          "restore",
      })

      setError(
        null
      )

      await adminExperienceService.restoreExperience(
        experience.id,
        {
          make_public:
            false,

          reason:
            "Experience restored from portfolio administration.",
        }
      )

      reloadExperiences()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The experience could not be restored."
      )
    } finally {
      setBusyExperience(
        null
      )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
            Professional history
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Manage experience
          </h1>

          <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
            Maintain professional roles,
            responsibilities, achievements,
            employment history and public
            portfolio visibility.
          </p>
        </div>

        <Button
          type="button"
          onClick={
            openCreate
          }
        >
          <Plus
            aria-hidden="true"
          />

          New experience
        </Button>
      </div>

      <AdminExperienceFilters
        filters={
          filters
        }
        onChange={
          changeFilters
        }
        onReset={
          resetFilters
        }
      />

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

      <div
        className={
          editor
            ? "grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(400px,0.75fr)]"
            : ""
        }
      >
        <div className="min-w-0">
          {loading ? (
            <div className="flex min-h-64 items-center justify-center rounded-2xl border border-border bg-background">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Loader2
                  className="size-5 animate-spin"
                  aria-hidden="true"
                />

                Loading experiences...
              </div>
            </div>
          ) : experiences &&
            experiences.items.length >
              0 ? (
            <div className="space-y-4">
              {experiences.items.map(
                (
                  experience
                ) => (
                  <AdminExperienceCard
                    key={
                      experience.id
                    }
                    experience={
                      experience
                    }
                    selected={
                      editor?.mode ===
                        "edit" &&
                      editor.experience.id ===
                        experience.id
                    }
                    busyAction={
                      busyExperience?.id ===
                      experience.id
                        ? busyExperience.action
                        : null
                    }
                    onEdit={
                      openEdit
                    }
                    onToggleVisibility={
                      toggleVisibility
                    }
                    onToggleFeatured={
                      toggleFeatured
                    }
                    onDelete={
                      deleteExperience
                    }
                    onRestore={
                      restoreExperience
                    }
                  />
                )
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
              <BriefcaseBusiness
                className="mx-auto size-8 text-muted-foreground"
                aria-hidden="true"
              />

              <h2 className="mt-4 font-semibold">
                No experiences found
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Change the current filters
                or add professional
                experience.
              </p>
            </div>
          )}

          {experiences &&
          experiences.total_pages >
            0 ? (
            <div className="mt-5 flex flex-col gap-3 rounded-xl border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-muted-foreground">
                Page{" "}
                {
                  experiences.page
                }{" "}
                of{" "}
                {
                  experiences.total_pages
                }{" "}
                ·{" "}
                {
                  experiences.total_items
                }{" "}
                experiences
              </p>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !experiences.has_previous_page ||
                    loading
                  }
                  onClick={() =>
                    changePage(
                      page - 1
                    )
                  }
                >
                  Previous
                </Button>

                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !experiences.has_next_page ||
                    loading
                  }
                  onClick={() =>
                    changePage(
                      page + 1
                    )
                  }
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </div>

        {editor ? (
          <div className="min-w-0 xl:sticky xl:top-6 xl:self-start">
            <AdminExperienceForm
              key={
                editor.mode ===
                "create"
                  ? "new-experience"
                  : editor.experience.id
              }
              experience={
                editor.experience
              }
              mode={
                editor.mode
              }
              onSaved={
                handleSaved
              }
              onCancel={
                closeEditor
              }
            />
          </div>
        ) : null}
      </div>
    </div>
  )
}