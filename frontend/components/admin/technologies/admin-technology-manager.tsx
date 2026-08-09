"use client"

import {
  AlertCircle,
  Cpu,
  Loader2,
  Plus,
} from "lucide-react"

import {
  useEffect,
  useState,
} from "react"

import {
  AdminTechnologyCard,
  type TechnologyBusyAction,
} from "@/components/admin/technologies/admin-technology-card"

import {
  AdminTechnologyFilters,
} from "@/components/admin/technologies/admin-technology-filters"

import {
  AdminTechnologyForm,
} from "@/components/admin/technologies/admin-technology-form"

import {
  defaultTechnologyAdminFilters,
  type TechnologyAdminFilterState,
} from "@/components/admin/technologies/technology-admin-filters"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminTechnologyService,
} from "@/services/admin"

import type {
  AdminProjectTechnologyListResponse,
  ProjectTechnologyAdminRead,
} from "@/types/portfolio/project-technology"

const PAGE_SIZE =
  10

const SEARCH_DEBOUNCE_MS =
  750

type EditorState =
  | {
      mode:
        "create"

      technology:
        null
    }
  | {
      mode:
        "edit"

      technology:
        ProjectTechnologyAdminRead
    }
  | null

export function AdminTechnologyManager() {
  const [
    technologies,
    setTechnologies,
  ] =
    useState<AdminProjectTechnologyListResponse | null>(
      null
    )

  const [
    filters,
    setFilters,
  ] =
    useState<TechnologyAdminFilterState>(
      defaultTechnologyAdminFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      defaultTechnologyAdminFilters.search
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
    busyTechnology,
    setBusyTechnology,
  ] =
    useState<{
      id: string

      action:
        TechnologyBusyAction
    } | null>(
      null
    )

  useEffect(() => {
    if (
      filters.search ===
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
    debouncedSearch,
  ])

  useEffect(() => {
    let cancelled =
      false

    const request =
      adminTechnologyService.getTechnologies(
        {
          page,

          page_size:
            PAGE_SIZE,

          search:
            debouncedSearch.trim() ||
            undefined,

          category:
            filters.category ===
            "all"
              ? undefined
              : filters.category,

          is_active:
            filters.status ===
            "all"
              ? undefined
              : filters.status ===
                "active",

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
          if (
            cancelled
          ) {
            return
          }

          setTechnologies(
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
              : "Technologies could not be loaded."
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
    filters.category,
    filters.status,
    filters.includeDeleted,
    filters.sortBy,
    filters.sortDirection,
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

  function reloadTechnologies() {
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
      TechnologyAdminFilterState
  ) {
    const searchChanged =
      nextFilters.search !==
      filters.search

    const nonSearchChanged =
      nextFilters.category !==
        filters.category ||
      nextFilters.status !==
        filters.status ||
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
    reloadTechnologies()

    setFilters(
      defaultTechnologyAdminFilters
    )

    setDebouncedSearch(
      defaultTechnologyAdminFilters.search
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

      technology:
        null,
    })
  }

  function openEdit(
    technology:
      ProjectTechnologyAdminRead
  ) {
    setError(
      null
    )

    setEditor({
      mode:
        "edit",

      technology,
    })
  }

  function closeEditor() {
    setEditor(
      null
    )
  }

  function handleSaved(
    technology:
      ProjectTechnologyAdminRead,
    created:
      boolean
  ) {
    setEditor({
      mode:
        "edit",

      technology,
    })

    if (
      created
    ) {
      setPage(
        1
      )
    }

    reloadTechnologies()
  }

  async function toggleStatus(
    technology:
      ProjectTechnologyAdminRead
  ) {
    if (
      busyTechnology ||
      technology.deleted_at
    ) {
      return
    }

    try {
      setBusyTechnology({
        id:
          technology.id,

        action:
          "status",
      })

      setError(
        null
      )

      const updated =
        await adminTechnologyService.updateStatus(
          technology.id,
          {
            is_active:
              !technology.is_active,

            reason:
              "Technology status updated from portfolio administration.",
          }
        )

      if (
        editor?.mode ===
          "edit" &&
        editor.technology.id ===
          technology.id
      ) {
        setEditor({
          mode:
            "edit",

          technology:
            updated,
        })
      }

      reloadTechnologies()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Technology status could not be updated."
      )
    } finally {
      setBusyTechnology(
        null
      )
    }
  }

  async function deleteTechnology(
    technology:
      ProjectTechnologyAdminRead
  ) {
    if (
      busyTechnology ||
      technology.deleted_at
    ) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${technology.name}"?\n\nTechnologies assigned to active projects cannot be deleted.`
      )

    if (
      !confirmed
    ) {
      return
    }

    try {
      setBusyTechnology({
        id:
          technology.id,

        action:
          "delete",
      })

      setError(
        null
      )

      await adminTechnologyService.deleteTechnology(
        technology.id,
        {
          reason:
            "Technology deleted from portfolio administration.",
        }
      )

      if (
        editor?.mode ===
          "edit" &&
        editor.technology.id ===
          technology.id
      ) {
        setEditor(
          null
        )
      }

      reloadTechnologies()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The technology could not be deleted."
      )
    } finally {
      setBusyTechnology(
        null
      )
    }
  }

  async function restoreTechnology(
    technology:
      ProjectTechnologyAdminRead
  ) {
    if (
      busyTechnology ||
      !technology.deleted_at
    ) {
      return
    }

    try {
      setBusyTechnology({
        id:
          technology.id,

        action:
          "restore",
      })

      setError(
        null
      )

      await adminTechnologyService.restoreTechnology(
        technology.id,
        {
          activate:
            true,

          reason:
            "Technology restored from portfolio administration.",
        }
      )

      reloadTechnologies()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The technology could not be restored."
      )
    } finally {
      setBusyTechnology(
        null
      )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
            Portfolio stack
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Manage technologies
          </h1>

          <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
            Maintain the languages,
            frameworks, tools, platforms
            and services used across your
            portfolio projects.
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

          New technology
        </Button>
      </div>

      <AdminTechnologyFilters
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
            ? "grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(380px,0.75fr)]"
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

                Loading technologies...
              </div>
            </div>
          ) : technologies &&
            technologies.items.length >
              0 ? (
            <div className="space-y-4">
              {technologies.items.map(
                (
                  technology
                ) => (
                  <AdminTechnologyCard
                    key={
                      technology.id
                    }
                    technology={
                      technology
                    }
                    selected={
                      editor?.mode ===
                        "edit" &&
                      editor.technology.id ===
                        technology.id
                    }
                    busyAction={
                      busyTechnology?.id ===
                      technology.id
                        ? busyTechnology.action
                        : null
                    }
                    onEdit={
                      openEdit
                    }
                    onToggleStatus={
                      toggleStatus
                    }
                    onDelete={
                      deleteTechnology
                    }
                    onRestore={
                      restoreTechnology
                    }
                  />
                )
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
              <Cpu
                className="mx-auto size-8 text-muted-foreground"
                aria-hidden="true"
              />

              <h2 className="mt-4 font-semibold">
                No technologies found
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Change the current filters
                or create a portfolio
                technology.
              </p>
            </div>
          )}

          {technologies &&
          technologies.total_pages >
            0 ? (
            <div className="mt-5 flex flex-col gap-3 rounded-xl border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-muted-foreground">
                Page{" "}
                {
                  technologies.page
                }{" "}
                of{" "}
                {
                  technologies.total_pages
                }{" "}
                ·{" "}
                {
                  technologies.total_items
                }{" "}
                technologies
              </p>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !technologies.has_previous_page ||
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
                    !technologies.has_next_page ||
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
            <AdminTechnologyForm
              key={
                editor.mode ===
                "create"
                  ? "new-technology"
                  : editor.technology.id
              }
              technology={
                editor.technology
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