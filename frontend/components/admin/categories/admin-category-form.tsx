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
  adminCategoryService,
} from "@/services/admin"

import type {
  ProjectCategoryAdminRead,
  ProjectCategoryCreate,
  ProjectCategoryUpdate,
} from "@/types/portfolio/project-category"

type AdminCategoryFormProps = {
  category:
    ProjectCategoryAdminRead | null

  mode:
    "create" | "edit"

  onSaved: (
    category:
      ProjectCategoryAdminRead,
    created:
      boolean
  ) => void

  onCancel: () => void
}

type CategoryFormState = {
  name: string
  slug: string

  description: string
  icon: string
  color: string

  sortOrder: string

  seoTitle: string
  seoDescription: string

  isActive: boolean
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

function categoryToForm(
  category:
    ProjectCategoryAdminRead | null
): CategoryFormState {
  return {
    name:
      category?.name ??
      "",

    slug:
      category?.slug ??
      "",

    description:
      category?.description ??
      "",

    icon:
      category?.icon ??
      "",

    color:
      category?.color ??
      "",

    sortOrder:
      String(
        category?.sort_order ??
          0
      ),

    seoTitle:
      category?.seo_title ??
      "",

    seoDescription:
      category?.seo_description ??
      "",

    isActive:
      category?.is_active ??
      true,
  }
}

export function AdminCategoryForm({
  category,
  mode,
  onSaved,
  onCancel,
}: AdminCategoryFormProps) {
  const [
    form,
    setForm,
  ] =
    useState<CategoryFormState>(
      () =>
        categoryToForm(
          category
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
    TKey extends keyof CategoryFormState,
  >(
    key:
      TKey,
    value:
      CategoryFormState[TKey]
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

  function buildCommonPayload() {
    const name =
      form.name.trim()

    const slug =
      slugify(
        form.slug
      )

    if (
      name.length <
      2
    ) {
      setError(
        "Category name must contain at least 2 characters."
      )

      return null
    }

    if (
      slug.length <
      2
    ) {
      setError(
        "Category slug must contain at least 2 characters."
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

    const color =
      nullable(
        form.color
      )

    if (
      color &&
      !/^#[0-9A-Fa-f]{6}$/.test(
        color
      )
    ) {
      setError(
        "Color must use a six-digit hexadecimal value such as #3366FF."
      )

      return null
    }

    return {
      name,
      slug,

      description:
        nullable(
          form.description
        ),

      icon:
        nullable(
          form.icon
        ),

      color:
        color?.toUpperCase() ??
        null,

      sort_order:
        sortOrder,

      seo_title:
        nullable(
          form.seoTitle
        ),

      seo_description:
        nullable(
          form.seoDescription
        ),
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
        ProjectCategoryAdminRead

      if (
        editing &&
        category
      ) {
        const payload:
          ProjectCategoryUpdate = {
          ...commonPayload,
        }

        updated =
          await adminCategoryService.updateCategory(
            category.id,
            payload
          )
      } else {
        const payload:
          ProjectCategoryCreate = {
          ...commonPayload,

          is_active:
            form.isActive,
        }

        updated =
          await adminCategoryService.createCategory(
            payload
          )
      }

      setForm(
        categoryToForm(
          updated
        )
      )

      setSuccess(
        editing
          ? "Category changes saved successfully."
          : "Category created successfully."
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
            ? "The category could not be updated."
            : "The category could not be created."
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
              ? "Edit category"
              : "New category"}
          </p>

          <h2 className="mt-2 text-xl font-semibold">
            {editing
              ? category?.name
              : "Create portfolio category"}
          </h2>

          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Manage taxonomy, presentation
            and search metadata.
          </p>
        </div>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={
            onCancel
          }
          aria-label="Close category editor"
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
              Name
            </span>

            <input
              value={
                form.name
              }
              onChange={(event) =>
                updateField(
                  "name",
                  event.target.value
                )
              }
              required
              minLength={2}
              maxLength={100}
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>

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
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 font-mono text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
        </div>

        <label className="block">
          <span className="text-sm font-medium">
            Description
          </span>

          <textarea
            value={
              form.description
            }
            onChange={(event) =>
              updateField(
                "description",
                event.target.value
              )
            }
            maxLength={2000}
            rows={6}
            className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          />

          <p className="mt-1 text-right text-xs text-muted-foreground">
            {
              form.description.length
            }
            /2000
          </p>
        </label>

        <div className="grid gap-5 sm:grid-cols-3">
          <label className="block">
            <span className="text-sm font-medium">
              Icon
            </span>

            <input
              value={
                form.icon
              }
              onChange={(event) =>
                updateField(
                  "icon",
                  event.target.value
                )
              }
              maxLength={100}
              placeholder="folder"
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Color
            </span>

            <div className="mt-2 flex gap-2">
              <input
                type="color"
                value={
                  /^#[0-9A-Fa-f]{6}$/.test(
                    form.color
                  )
                    ? form.color
                    : "#3366FF"
                }
                onChange={(event) =>
                  updateField(
                    "color",
                    event.target.value.toUpperCase()
                  )
                }
                className="h-11 w-12 rounded-lg border border-input bg-background p-1"
              />

              <input
                value={
                  form.color
                }
                onChange={(event) =>
                  updateField(
                    "color",
                    event.target.value.toUpperCase()
                  )
                }
                maxLength={7}
                placeholder="#3366FF"
                className="h-11 min-w-0 flex-1 rounded-lg border border-input bg-background px-3 font-mono text-sm"
              />
            </div>
          </label>

          <label className="block">
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
        </div>

        {!editing ? (
          <label className="flex w-fit cursor-pointer items-center gap-3 text-sm">
            <input
              type="checkbox"
              checked={
                form.isActive
              }
              onChange={(event) =>
                updateField(
                  "isActive",
                  event.target.checked
                )
              }
              className="size-4 rounded border-input"
            />

            Create as active category
          </label>
        ) : (
          <p className="text-xs leading-5 text-muted-foreground">
            Active/inactive state is managed
            separately from category content.
          </p>
        )}

        <div className="border-t border-border pt-6">
          <h3 className="font-medium">
            Search metadata
          </h3>

          <div className="mt-4 grid gap-5">
            <label className="block">
              <span className="text-sm font-medium">
                SEO title
              </span>

              <input
                value={
                  form.seoTitle
                }
                onChange={(event) =>
                  updateField(
                    "seoTitle",
                    event.target.value
                  )
                }
                maxLength={70}
                className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm"
              />

              <p className="mt-1 text-right text-xs text-muted-foreground">
                {
                  form.seoTitle.length
                }
                /70
              </p>
            </label>

            <label className="block">
              <span className="text-sm font-medium">
                SEO description
              </span>

              <textarea
                value={
                  form.seoDescription
                }
                onChange={(event) =>
                  updateField(
                    "seoDescription",
                    event.target.value
                  )
                }
                maxLength={170}
                rows={4}
                className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm"
              />

              <p className="mt-1 text-right text-xs text-muted-foreground">
                {
                  form.seoDescription.length
                }
                /170
              </p>
            </label>
          </div>
        </div>
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
              : "Create category"}
        </Button>
      </div>
    </form>
  )
}