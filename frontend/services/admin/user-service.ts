import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminUserDeleteRequest,
  AdminUserDetail,
  AdminUserListParams,
  AdminUserListResponse,
  AdminUserRestoreRequest,
  AdminUserStatusUpdate,
} from "@/types/admin-user"

function buildQueryString(
  params:
    AdminUserListParams
): string {
  const searchParams =
    new URLSearchParams()

  const entries: Array<
    [
      string,
      string |
        number |
        boolean |
        undefined,
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
      "status",
      params.status,
    ],
    [
      "is_verified",
      params.is_verified,
    ],
    [
      "is_superuser",
      params.is_superuser,
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

function userPath(
  userId: string
): string {
  return `/api/admin/users/${encodeURIComponent(
    userId
  )}`
}

export const adminUserService = {
  getUsers(
    params:
      AdminUserListParams = {}
  ): Promise<AdminUserListResponse> {
    return adminRequest<AdminUserListResponse>(
      `/api/admin/users${buildQueryString(
        params
      )}`
    )
  },

  getUser(
    userId: string,
    {
      includeDeleted = false,
    }: {
      includeDeleted?: boolean
    } = {}
  ): Promise<AdminUserDetail> {
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

    return adminRequest<AdminUserDetail>(
      `${userPath(
        userId
      )}${query ? `?${query}` : ""}`
    )
  },

  updateStatus(
    userId: string,
    payload:
      AdminUserStatusUpdate
  ): Promise<AdminUserDetail> {
    return adminRequest<AdminUserDetail>(
      `${userPath(
        userId
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

  deleteUser(
    userId: string,
    payload:
      AdminUserDeleteRequest = {}
  ): Promise<AdminUserDetail> {
    return adminRequest<AdminUserDetail>(
      userPath(
        userId
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

  restoreUser(
    userId: string,
    payload:
      AdminUserRestoreRequest = {}
  ): Promise<AdminUserDetail> {
    return adminRequest<AdminUserDetail>(
      `${userPath(
        userId
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