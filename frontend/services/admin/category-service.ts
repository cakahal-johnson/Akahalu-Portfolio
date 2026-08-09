import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminProjectCategoryListParams,
  AdminProjectCategoryListResponse,
  ProjectCategoryAdminRead,
  ProjectCategoryCreate,
  ProjectCategoryDeleteRequest,
  ProjectCategoryRestoreRequest,
  ProjectCategoryStatusUpdate,
  ProjectCategoryUpdate,
} from "@/types/portfolio/project-category"

function buildQueryString(
  params: AdminProjectCategoryListParams
): string {
  const searchParams =
    new URLSearchParams()

  const entries: Array<
    [
      string,
      string | number | boolean | undefined,
    ]
  > = [
    [
      "page",
      params.page,
    ],
    [
      "page_size",
      params.page_size,
    ],
    [
      "search",
      params.search,
    ],
    [
      "is_active",
      params.is_active,
    ],
    [
      "include_deleted",
      params.include_deleted,
    ],
    [
      "sort_by",
      params.sort_by,
    ],
    [
      "sort_direction",
      params.sort_direction,
    ],
  ]

  for (
    const [
      key,
      value,
    ] of entries
  ) {
    if (
      value === undefined ||
      value === ""
    ) {
      continue
    }

    searchParams.set(
      key,
      String(value)
    )
  }

  const query =
    searchParams.toString()

  return query
    ? `?${query}`
    : ""
}

function categoryPath(
  categoryId: string
): string {
  return `/api/admin/categories/${encodeURIComponent(
    categoryId
  )}`
}

export const adminCategoryService = {
  getCategories(
    params: AdminProjectCategoryListParams = {}
  ): Promise<AdminProjectCategoryListResponse> {
    return adminRequest<AdminProjectCategoryListResponse>(
      `/api/admin/categories${buildQueryString(
        params
      )}`
    )
  },

  getCategory(
    categoryId: string,
    {
      includeDeleted = false,
    }: {
      includeDeleted?: boolean
    } = {}
  ): Promise<ProjectCategoryAdminRead> {
    const searchParams =
      new URLSearchParams()

    if (includeDeleted) {
      searchParams.set(
        "include_deleted",
        "true"
      )
    }

    const query =
      searchParams.toString()

    return adminRequest<ProjectCategoryAdminRead>(
      `${categoryPath(
        categoryId
      )}${query ? `?${query}` : ""}`
    )
  },

  createCategory(
    payload: ProjectCategoryCreate
  ): Promise<ProjectCategoryAdminRead> {
    return adminRequest<ProjectCategoryAdminRead>(
      "/api/admin/categories",
      {
        method: "POST",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  updateCategory(
    categoryId: string,
    payload: ProjectCategoryUpdate
  ): Promise<ProjectCategoryAdminRead> {
    return adminRequest<ProjectCategoryAdminRead>(
      categoryPath(
        categoryId
      ),
      {
        method: "PATCH",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  updateStatus(
    categoryId: string,
    payload: ProjectCategoryStatusUpdate
  ): Promise<ProjectCategoryAdminRead> {
    return adminRequest<ProjectCategoryAdminRead>(
      `${categoryPath(
        categoryId
      )}/status`,
      {
        method: "PATCH",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  deleteCategory(
    categoryId: string,
    payload: ProjectCategoryDeleteRequest = {}
  ): Promise<ProjectCategoryAdminRead> {
    return adminRequest<ProjectCategoryAdminRead>(
      categoryPath(
        categoryId
      ),
      {
        method: "DELETE",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  restoreCategory(
    categoryId: string,
    payload: ProjectCategoryRestoreRequest = {}
  ): Promise<ProjectCategoryAdminRead> {
    return adminRequest<ProjectCategoryAdminRead>(
      `${categoryPath(
        categoryId
      )}/restore`,
      {
        method: "POST",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },
} as const