import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminProjectTechnologyListParams,
  AdminProjectTechnologyListResponse,
  ProjectTechnologyAdminRead,
  ProjectTechnologyCreate,
  ProjectTechnologyDeleteRequest,
  ProjectTechnologyRestoreRequest,
  ProjectTechnologyStatusUpdate,
  ProjectTechnologyUpdate,
} from "@/types/portfolio/project-technology"

function buildQueryString(
  params:
    AdminProjectTechnologyListParams
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
      "category",
      params.category,
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
      String(
        value
      )
    )
  }

  const query =
    searchParams.toString()

  return query
    ? `?${query}`
    : ""
}

function technologyPath(
  technologyId: string
): string {
  return `/api/admin/technologies/${encodeURIComponent(
    technologyId
  )}`
}

export const adminTechnologyService = {
  getTechnologies(
    params:
      AdminProjectTechnologyListParams = {}
  ): Promise<AdminProjectTechnologyListResponse> {
    return adminRequest<AdminProjectTechnologyListResponse>(
      `/api/admin/technologies${buildQueryString(
        params
      )}`
    )
  },

  getTechnology(
    technologyId: string,
    {
      includeDeleted = false,
    }: {
      includeDeleted?: boolean
    } = {}
  ): Promise<ProjectTechnologyAdminRead> {
    const searchParams =
      new URLSearchParams()

    if (
      includeDeleted
    ) {
      searchParams.set(
        "include_deleted",
        "true"
      )
    }

    const query =
      searchParams.toString()

    return adminRequest<ProjectTechnologyAdminRead>(
      `${technologyPath(
        technologyId
      )}${query ? `?${query}` : ""}`
    )
  },

  createTechnology(
    payload:
      ProjectTechnologyCreate
  ): Promise<ProjectTechnologyAdminRead> {
    return adminRequest<ProjectTechnologyAdminRead>(
      "/api/admin/technologies",
      {
        method:
          "POST",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  updateTechnology(
    technologyId: string,
    payload:
      ProjectTechnologyUpdate
  ): Promise<ProjectTechnologyAdminRead> {
    return adminRequest<ProjectTechnologyAdminRead>(
      technologyPath(
        technologyId
      ),
      {
        method:
          "PATCH",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  updateStatus(
    technologyId: string,
    payload:
      ProjectTechnologyStatusUpdate
  ): Promise<ProjectTechnologyAdminRead> {
    return adminRequest<ProjectTechnologyAdminRead>(
      `${technologyPath(
        technologyId
      )}/status`,
      {
        method:
          "PATCH",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  deleteTechnology(
    technologyId: string,
    payload:
      ProjectTechnologyDeleteRequest = {}
  ): Promise<ProjectTechnologyAdminRead> {
    return adminRequest<ProjectTechnologyAdminRead>(
      technologyPath(
        technologyId
      ),
      {
        method:
          "DELETE",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },

  restoreTechnology(
    technologyId: string,
    payload:
      ProjectTechnologyRestoreRequest = {}
  ): Promise<ProjectTechnologyAdminRead> {
    return adminRequest<ProjectTechnologyAdminRead>(
      `${technologyPath(
        technologyId
      )}/restore`,
      {
        method:
          "POST",

        body:
          JSON.stringify(
            payload
          ),
      }
    )
  },
} as const