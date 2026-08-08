"use client"

import {
  AlertCircle,
  FolderKanban,
  Loader2,
  Plus,
} from "lucide-react"
import Link from "next/link"
import {
  useEffect,
  useState,
} from "react"

import { AdminProjectCard } from "@/components/admin/projects/admin-project-card"
import { AdminProjectFilters } from "@/components/admin/projects/admin-project-filters"
import { AdminProjectPagination } from "@/components/admin/projects/admin-project-pagination"
import {
  defaultProjectAdminFilters,
  type ProjectAdminFilterState,
} from "@/components/admin/projects/project-admin-filters"

import { Button } from "@/components/ui/button"

import {
  AdminApiError,
  adminProjectService,
} from "@/services/admin"

import {
  publicPortfolioService,
} from "@/services/portfolio"

import type {
  AdminProjectListResponse,
  ProjectAdminRead,
} from "@/types/portfolio/project"

import type {
  ProjectCategoryRead,
  ProjectTechnologyRead,
} from "@/types/portfolio"

const PAGE_SIZE = 10
const SEARCH_DEBOUNCE_MS = 750

export function AdminProjectManager() {
  const [
    projects,
    setProjects,
  ] =
    useState<AdminProjectListResponse | null>(
      null
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
    filters,
    setFilters,
  ] =
    useState<ProjectAdminFilterState>(
      defaultProjectAdminFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      defaultProjectAdminFilters.search
    )

  const [
    page,
    setPage,
  ] =
    useState(1)

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
    busyProject,
    setBusyProject,
  ] =
    useState<{
      id: string
      action:
        | "visibility"
        | "featured"
    } | null>(null)

  useEffect(() => {
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
            filters.search
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
    filters.search,
  ])

  useEffect(() => {
    let cancelled =
      false

    const request =
      adminProjectService.getProjects(
        {
          page,

          page_size:
            PAGE_SIZE,

          search:
            debouncedSearch.trim() ||
            undefined,

          category_id:
            filters.categoryId ||
            undefined,

          technology_id:
            filters.technologyId ||
            undefined,

          project_status:
            filters.status ||
            undefined,

          visibility:
            filters.visibility ||
            undefined,

          is_featured:
            filters.featured ===
            "all"
              ? undefined
              : filters.featured ===
                "true",

          include_deleted:
            filters.includeDeleted,

          sort_by:
            filters.sortBy,

          sort_direction:
            filters.sortDirection,
        }
      )

    void request
      .then(
        (result) => {
          if (cancelled) {
            return
          }

          setProjects(
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
          if (cancelled) {
            return
          }

          setError(
            caughtError instanceof
            AdminApiError
              ? caughtError.message
              : "Projects could not be loaded."
          )
        }
      )
      .finally(
        () => {
          if (cancelled) {
            return
          }

          setLoading(
            false
          )
        }
      )

    return () => {
      cancelled = true
    }
  }, [
    page,
    debouncedSearch,
    filters.categoryId,
    filters.technologyId,
    filters.status,
    filters.visibility,
    filters.featured,
    filters.includeDeleted,
    filters.sortBy,
    filters.sortDirection,
  ])

  useEffect(() => {
    let cancelled =
      false

    async function loadFilterOptions() {
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
    }

    void loadFilterOptions()

    return () => {
      cancelled = true
    }
  }, [])

  function beginProjectReload() {
    setLoading(
      true
    )

    setError(
      null
    )
  }

  function changeFilters(
    nextFilters: ProjectAdminFilterState
  ) {
    const searchChanged =
      nextFilters.search !==
      filters.search

    const nonSearchFilterChanged =
      nextFilters.categoryId !==
        filters.categoryId ||
      nextFilters.technologyId !==
        filters.technologyId ||
      nextFilters.status !==
        filters.status ||
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
      nonSearchFilterChanged
    ) {
      beginProjectReload()

      /*
       * If a user changes another filter
       * while a search debounce is pending,
       * immediately apply the latest search
       * value to the new filter request.
       */
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

    /*
     * Search-only changes deliberately do
     * not change page/loading here.
     * The debounce callback performs those
     * updates after the user pauses typing.
     */
    if (
      searchChanged &&
      !nonSearchFilterChanged
    ) {
      return
    }
  }

  function resetFilters() {
    beginProjectReload()

    setFilters(
      defaultProjectAdminFilters
    )

    setDebouncedSearch(
      defaultProjectAdminFilters.search
    )

    setPage(
      1
    )
  }

  function changePage(
    nextPage: number
  ) {
    if (
      nextPage === page
    ) {
      return
    }

    beginProjectReload()

    setPage(
      nextPage
    )
  }

  function replaceProject(
    updated: ProjectAdminRead
  ) {
    setProjects(
      (current) => {
        if (!current) {
          return current
        }

        return {
          ...current,

          items:
            current.items.map(
              (project) =>
                project.id ===
                updated.id
                  ? updated
                  : project
            ),
        }
      }
    )
  }

  async function toggleVisibility(
    project: ProjectAdminRead
  ) {
    if (busyProject) {
      return
    }

    try {
      setBusyProject({
        id:
          project.id,

        action:
          "visibility",
      })

      setError(
        null
      )

      const updated =
        await adminProjectService.updateVisibility(
          project.id,
          {
            visibility:
              project.visibility ===
              "public"
                ? "private"
                : "public",

            reason:
              "Visibility updated from portfolio administration.",
          }
        )

      replaceProject(
        updated
      )
    } catch (caughtError) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Project visibility could not be updated."
      )
    } finally {
      setBusyProject(
        null
      )
    }
  }

  async function toggleFeatured(
    project: ProjectAdminRead
  ) {
    if (busyProject) {
      return
    }

    try {
      setBusyProject({
        id:
          project.id,

        action:
          "featured",
      })

      setError(
        null
      )

      const updated =
        await adminProjectService.updateFeatured(
          project.id,
          {
            is_featured:
              !project.is_featured,

            reason:
              "Featured status updated from portfolio administration.",
          }
        )

      replaceProject(
        updated
      )
    } catch (caughtError) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Featured status could not be updated."
      )
    } finally {
      setBusyProject(
        null
      )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
            Portfolio projects
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Manage projects
          </h1>

          <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
            Search, filter and manage
            projects displayed throughout
            the portfolio.
          </p>
        </div>

        <Button
          asChild
        >
          <Link href="/admin/projects/new">
            <Plus
              aria-hidden="true"
            />

            New project
          </Link>
        </Button>
      </div>

      <AdminProjectFilters
        filters={
          filters
        }
        categories={
          categories
        }
        technologies={
          technologies
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

      {loading ? (
        <div className="flex min-h-64 items-center justify-center rounded-2xl border border-border bg-background">
          <div className="flex items-center gap-3 text-sm text-muted-foreground">
            <Loader2
              className="size-5 animate-spin"
              aria-hidden="true"
            />

            Loading projects...
          </div>
        </div>
      ) : projects &&
        projects.items.length >
          0 ? (
        <div className="space-y-4">
          {projects.items.map(
            (project) => (
              <AdminProjectCard
                key={
                  project.id
                }
                project={
                  project
                }
                busyAction={
                  busyProject?.id ===
                  project.id
                    ? busyProject.action
                    : null
                }
                onToggleVisibility={
                  toggleVisibility
                }
                onToggleFeatured={
                  toggleFeatured
                }
              />
            )
          )}
        </div>
      ) : (
        <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
          <FolderKanban
            className="mx-auto size-8 text-muted-foreground"
            aria-hidden="true"
          />

          <h2 className="mt-4 font-semibold">
            No projects found
          </h2>

          <p className="mt-2 text-sm text-muted-foreground">
            Change your filters or create
            a new portfolio project.
          </p>
        </div>
      )}

      {projects ? (
        <AdminProjectPagination
          page={
            projects.page
          }
          totalPages={
            projects.total_pages
          }
          totalItems={
            projects.total_items
          }
          hasNextPage={
            projects.has_next_page
          }
          hasPreviousPage={
            projects.has_previous_page
          }
          onPageChange={
            changePage
          }
        />
      ) : null}
    </div>
  )
}