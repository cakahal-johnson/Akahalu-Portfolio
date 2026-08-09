import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminExperienceListParams,
  AdminExperienceListResponse,
  ExperienceAdminRead,
  ExperienceCreate,
  ExperienceDeleteRequest,
  ExperienceFeaturedUpdate,
  ExperienceRestoreRequest,
  ExperienceUpdate,
  ExperienceVisibilityUpdate,
} from "@/types/portfolio/experience"

function buildQueryString(
  params:
    AdminExperienceListParams
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
      "employment_type",
      params.employment_type,
    ],
    [
      "location_type",
      params.location_type,
    ],
    [
      "is_current",
      params.is_current,
    ],
    [
      "is_public",
      params.is_public,
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

function experiencePath(
  experienceId: string
): string {
  return `/api/admin/experiences/${encodeURIComponent(
    experienceId
  )}`
}

export const adminExperienceService = {
  getExperiences(
    params:
      AdminExperienceListParams = {}
  ): Promise<AdminExperienceListResponse> {
    return adminRequest<AdminExperienceListResponse>(
      `/api/admin/experiences${buildQueryString(
        params
      )}`
    )
  },

  getExperience(
    experienceId: string,
    {
      includeDeleted = false,
    }: {
      includeDeleted?: boolean
    } = {}
  ): Promise<ExperienceAdminRead> {
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

    return adminRequest<ExperienceAdminRead>(
      `${experiencePath(
        experienceId
      )}${query ? `?${query}` : ""}`
    )
  },

  createExperience(
    payload:
      ExperienceCreate
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      "/api/admin/experiences",
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

  updateExperience(
    experienceId: string,
    payload:
      ExperienceUpdate
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      experiencePath(
        experienceId
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

  updateVisibility(
    experienceId: string,
    payload:
      ExperienceVisibilityUpdate
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      `${experiencePath(
        experienceId
      )}/visibility`,
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

  updateFeatured(
    experienceId: string,
    payload:
      ExperienceFeaturedUpdate
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      `${experiencePath(
        experienceId
      )}/featured`,
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

  deleteExperience(
    experienceId: string,
    payload:
      ExperienceDeleteRequest = {}
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      experiencePath(
        experienceId
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

  restoreExperience(
    experienceId: string,
    payload:
      ExperienceRestoreRequest = {}
  ): Promise<ExperienceAdminRead> {
    return adminRequest<ExperienceAdminRead>(
      `${experiencePath(
        experienceId
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