"use client"

import {
  AlertCircle,
  FolderTree,
  Loader2,
  Plus,
} from "lucide-react"
import {
  useEffect,
  useState,
} from "react"

import {
  AdminCategoryCard,
  type CategoryBusyAction,
} from "@/components/admin/categories/admin-category-card"

import {
  AdminCategoryFilters,
} from "@/components/admin/categories/admin-category-filters"

import {
  AdminCategoryForm,
} from "@/components/admin/categories/admin-category-form"

import {
  defaultCategoryAdminFilters,
  type CategoryAdminFilterState,
} from "@/components/admin/categories/category-admin-filters"

import {
  Button,
} from "@/components/ui/button"

import {
  AdminApiError,
  adminCategoryService,
} from "@/services/admin"

import type {
  AdminProjectCategoryListResponse,
  ProjectCategoryAdminRead,
} from "@/types/portfolio/project-category"

const PAGE_SIZE =
  10

const SEARCH_DEBOUNCE_MS =
  750

type EditorState =
  | {
      mode:
        "create"

      category:
        null
    }
  | {
      mode:
        "edit"

      category:
        ProjectCategoryAdminRead
    }
  | null

export function AdminCategoryManager() {
  const [
    categories,
    setCategories,
  ] =
    useState<AdminProjectCategoryListResponse | null>(
      null
    )

  const [
    filters,
    setFilters,
  ] =
    useState<CategoryAdminFilterState>(
      defaultCategoryAdminFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      defaultCategoryAdminFilters.search
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
    busyCategory,
    setBusyCategory,
  ] =
    useState<{
      id: string
      action:
        CategoryBusyAction
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
      adminCategoryService.getCategories(
        {
          page,

          page_size:
            PAGE_SIZE,

          search:
            debouncedSearch.trim() ||
            undefined,

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

          setCategories(
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
              : "Categories could not be loaded."
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

  function reloadCategories() {
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
      CategoryAdminFilterState
  ) {
    const searchChanged =
      nextFilters.search !==
      filters.search

    const nonSearchChanged =
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
    reloadCategories()

    setFilters(
      defaultCategoryAdminFilters
    )

    setDebouncedSearch(
      defaultCategoryAdminFilters.search
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

      category:
        null,
    })
  }

  function openEdit(
    category:
      ProjectCategoryAdminRead
  ) {
    setError(
      null
    )

    setEditor({
      mode:
        "edit",

      category,
    })
  }

  function closeEditor() {
    setEditor(
      null
    )
  }

  function handleSaved(
    category:
      ProjectCategoryAdminRead,
    created:
      boolean
  ) {
    setEditor({
      mode:
        "edit",

      category,
    })

    if (
      created
    ) {
      setPage(
        1
      )
    }

    reloadCategories()
  }

  async function toggleStatus(
    category:
      ProjectCategoryAdminRead
  ) {
    if (
      busyCategory ||
      category.deleted_at
    ) {
      return
    }

    try {
      setBusyCategory({
        id:
          category.id,

        action:
          "status",
      })

      setError(
        null
      )

      const updated =
        await adminCategoryService.updateStatus(
          category.id,
          {
            is_active:
              !category.is_active,

            reason:
              "Category status updated from portfolio administration.",
          }
        )

      if (
        editor?.mode ===
          "edit" &&
        editor.category.id ===
          category.id
      ) {
        setEditor({
          mode:
            "edit",

          category:
            updated,
        })
      }

      reloadCategories()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Category status could not be updated."
      )
    } finally {
      setBusyCategory(
        null
      )
    }
  }

    async function deleteCategory(
    category:
      ProjectCategoryAdminRead
  ) {
    if (
      busyCategory ||
      category.deleted_at
    ) {
      return
    }

    const confirmed =
      window.confirm(
        `Delete "${category.name}"?\n\nCategories assigned to active projects cannot be deleted.`
      )

    if (
      !confirmed
    ) {
      return
    }

    try {
      setBusyCategory({
        id:
          category.id,

        action:
          "delete",
      })

      setError(
        null
      )

      await adminCategoryService.deleteCategory(
        category.id,
        {
          reason:
            "Category deleted from portfolio administration.",
        }
      )

      if (
        editor?.mode ===
          "edit" &&
        editor.category.id ===
          category.id
      ) {
        setEditor(
          null
        )
      }

      reloadCategories()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The category could not be deleted."
      )
    } finally {
      setBusyCategory(
        null
      )
    }
  }

  async function restoreCategory(
    category:
      ProjectCategoryAdminRead
  ) {
    if (
      busyCategory ||
      !category.deleted_at
    ) {
      return
    }

    try {
      setBusyCategory({
        id:
          category.id,

        action:
          "restore",
      })

      setError(
        null
      )

      await adminCategoryService.restoreCategory(
        category.id,
        {
          activate:
            true,

          reason:
            "Category restored from portfolio administration.",
        }
      )

      reloadCategories()
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The category could not be restored."
      )
    } finally {
      setBusyCategory(
        null
      )
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
            Portfolio taxonomy
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Manage categories
          </h1>

          <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
            Organize portfolio projects
            into reusable categories and
            manage their public
            presentation.
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

          New category
        </Button>
      </div>

      <AdminCategoryFilters
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

                Loading categories...
              </div>
            </div>
          ) : categories &&
            categories.items.length >
              0 ? (
            <div className="space-y-4">
              {categories.items.map(
                (
                  category
                ) => (
                  <AdminCategoryCard
                    key={
                      category.id
                    }
                    category={
                      category
                    }
                    selected={
                      editor?.mode ===
                        "edit" &&
                      editor.category.id ===
                        category.id
                    }
                    busyAction={
                      busyCategory?.id ===
                      category.id
                        ? busyCategory.action
                        : null
                    }
                    onEdit={
                      openEdit
                    }
                    onToggleStatus={
                      toggleStatus
                    }
                    onDelete={
                      deleteCategory
                    }
                    onRestore={
                      restoreCategory
                    }
                  />
                )
              )}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border bg-background p-10 text-center">
              <FolderTree
                className="mx-auto size-8 text-muted-foreground"
                aria-hidden="true"
              />

              <h2 className="mt-4 font-semibold">
                No categories found
              </h2>

              <p className="mt-2 text-sm text-muted-foreground">
                Change the current filters
                or create a portfolio
                category.
              </p>
            </div>
          )}

          {categories &&
          categories.total_pages >
            0 ? (
            <div className="mt-5 flex flex-col gap-3 rounded-xl border border-border bg-background p-4 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm text-muted-foreground">
                Page{" "}
                {
                  categories.page
                }{" "}
                of{" "}
                {
                  categories.total_pages
                }{" "}
                ·{" "}
                {
                  categories.total_items
                }{" "}
                categories
              </p>

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  disabled={
                    !categories.has_previous_page ||
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
                    !categories.has_next_page ||
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
            <AdminCategoryForm
              key={
                editor.mode ===
                "create"
                  ? "new-category"
                  : editor.category.id
              }
              category={
                editor.category
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