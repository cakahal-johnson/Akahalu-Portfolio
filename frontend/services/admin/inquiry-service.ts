import {
  adminRequest,
} from "@/services/admin/client"

import type {
  AdminContactInquiryListParams,
  AdminContactInquiryListResponse,
  ContactInquiryAdminRead,
  ContactInquiryAssigneeOption,
  ContactInquiryDeleteRequest,
  ContactInquiryProjectOption,
  ContactInquiryReadUpdate,
  ContactInquiryRestoreRequest,
  ContactInquiryStatistics,
  ContactInquiryStatusUpdate,
  ContactInquiryUpdate,
} from "@/types/contact"

function buildQueryString(
  params:
    AdminContactInquiryListParams
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
      "inquiry_type",
      params.inquiry_type,
    ],
    [
      "inquiry_status",
      params.inquiry_status,
    ],
    [
      "priority",
      params.priority,
    ],
    [
      "is_read",
      params.is_read,
    ],
    [
      "assigned_to_id",
      params.assigned_to_id,
    ],
    [
      "project_id",
      params.project_id,
    ],
    [
      "include_unassigned",
      params.include_unassigned,
    ],
    [
      "include_deleted",
      params.include_deleted,
    ],
    [
      "created_from",
      params.created_from,
    ],
    [
      "created_to",
      params.created_to,
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

function inquiryPath(
  inquiryId: string
): string {
  return `/api/admin/inquiries/${encodeURIComponent(
    inquiryId
  )}`
}

export const adminInquiryService = {
  getStatistics():
    Promise<ContactInquiryStatistics> {
    return adminRequest<ContactInquiryStatistics>(
      "/api/admin/inquiries/statistics"
    )
  },

    getAssignees():
    Promise<ContactInquiryAssigneeOption[]> {
    return adminRequest<
      ContactInquiryAssigneeOption[]
    >(
      "/api/admin/inquiries/assignees"
    )
  },

  getProjects():
    Promise<ContactInquiryProjectOption[]> {
    return adminRequest<
      ContactInquiryProjectOption[]
    >(
      "/api/admin/inquiries/projects"
    )
  },

  getInquiries(
    params:
      AdminContactInquiryListParams = {}
  ): Promise<AdminContactInquiryListResponse> {
    return adminRequest<AdminContactInquiryListResponse>(
      `/api/admin/inquiries${buildQueryString(
        params
      )}`
    )
  },

  getInquiry(
    inquiryId: string,
    {
      includeDeleted = false,
    }: {
      includeDeleted?: boolean
    } = {}
  ): Promise<ContactInquiryAdminRead> {
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

    return adminRequest<ContactInquiryAdminRead>(
      `${inquiryPath(
        inquiryId
      )}${query ? `?${query}` : ""}`
    )
  },

  updateInquiry(
    inquiryId: string,
    payload:
      ContactInquiryUpdate
  ): Promise<ContactInquiryAdminRead> {
    return adminRequest<ContactInquiryAdminRead>(
      inquiryPath(
        inquiryId
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

  updateReadState(
    inquiryId: string,
    payload:
      ContactInquiryReadUpdate
  ): Promise<ContactInquiryAdminRead> {
    return adminRequest<ContactInquiryAdminRead>(
      `${inquiryPath(
        inquiryId
      )}/read-state`,
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
    inquiryId: string,
    payload:
      ContactInquiryStatusUpdate
  ): Promise<ContactInquiryAdminRead> {
    return adminRequest<ContactInquiryAdminRead>(
      `${inquiryPath(
        inquiryId
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

  deleteInquiry(
    inquiryId: string,
    payload:
      ContactInquiryDeleteRequest = {}
  ): Promise<ContactInquiryAdminRead> {
    return adminRequest<ContactInquiryAdminRead>(
      inquiryPath(
        inquiryId
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

  restoreInquiry(
    inquiryId: string,
    payload:
      ContactInquiryRestoreRequest = {}
  ): Promise<ContactInquiryAdminRead> {
    return adminRequest<ContactInquiryAdminRead>(
      `${inquiryPath(
        inquiryId
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