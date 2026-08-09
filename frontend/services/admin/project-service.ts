import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminProjectListParams,
  AdminProjectListResponse,
  ProjectAdminRead,
  ProjectCreate,
  ProjectFeaturedUpdate,
  ProjectStatusUpdate,
  ProjectUpdate,
  ProjectVisibilityUpdate,
} from "@/types/portfolio/project"

function buildQueryString(
  params: AdminProjectListParams
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
      "category_id",
      params.category_id,
    ],
    [
      "technology_id",
      params.technology_id,
    ],
    [
      "project_status",
      params.project_status,
    ],
    [
      "visibility",
      params.visibility,
    ],
    [
      "is_featured",
      params.is_featured,
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

function projectPath(
  projectId: string
): string {
  return `/api/admin/projects/${encodeURIComponent(
    projectId
  )}`
}

export const adminProjectService =
  {
    getProjects(
      params: AdminProjectListParams = {}
    ): Promise<AdminProjectListResponse> {
      return adminRequest<AdminProjectListResponse>(
        `/api/admin/projects${buildQueryString(
          params
        )}`
      )
    },

    getProject(
      projectId: string,
      {
        includeDeleted = false,
      }: {
        includeDeleted?: boolean
      } = {}
    ): Promise<ProjectAdminRead> {
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

      return adminRequest<ProjectAdminRead>(
        `${projectPath(
          projectId
        )}${query ? `?${query}` : ""}`
      )
    },

    createProject(
      payload: ProjectCreate
    ): Promise<ProjectAdminRead> {
      return adminRequest<ProjectAdminRead>(
        "/api/admin/projects",
        {
          method: "POST",
          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },

    updateProject(
      projectId: string,
      payload: ProjectUpdate
    ): Promise<ProjectAdminRead> {
      return adminRequest<ProjectAdminRead>(
        projectPath(
          projectId
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
      projectId: string,
      payload: ProjectStatusUpdate
    ): Promise<ProjectAdminRead> {
      return adminRequest<ProjectAdminRead>(
        `${projectPath(
          projectId
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

    updateVisibility(
      projectId: string,
      payload: ProjectVisibilityUpdate
    ): Promise<ProjectAdminRead> {
      return adminRequest<ProjectAdminRead>(
        `${projectPath(
          projectId
        )}/visibility`,
        {
          method: "PATCH",

          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },

    updateFeatured(
      projectId: string,
      payload: ProjectFeaturedUpdate
    ): Promise<ProjectAdminRead> {
      return adminRequest<ProjectAdminRead>(
        `${projectPath(
          projectId
        )}/featured`,
        {
          method: "PATCH",

          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },
  } as const