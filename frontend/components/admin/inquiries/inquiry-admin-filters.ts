import type {
  AdminContactInquirySortDirection,
  AdminContactInquirySortField,
  ContactInquiryPriority,
  ContactInquiryStatus,
  ContactInquiryType,
} from "@/types/contact"

export type InquiryTypeFilter =
  | "all"
  | ContactInquiryType

export type InquiryStatusFilter =
  | "all"
  | ContactInquiryStatus

export type InquiryPriorityFilter =
  | "all"
  | ContactInquiryPriority

export type InquiryReadFilter =
  | "all"
  | "read"
  | "unread"

export type InquiryAssignmentFilter =
  | "all"
  | "unassigned"
  | string

export type InquiryProjectFilter =
  | "all"
  | string

export type InquiryAdminFilters = {
  search: string

  inquiryType:
    InquiryTypeFilter

  status:
    InquiryStatusFilter

  priority:
    InquiryPriorityFilter

  readState:
    InquiryReadFilter

  assignment:
    InquiryAssignmentFilter

  project:
    InquiryProjectFilter

  createdFrom: string
  createdTo: string

  includeDeleted: boolean

  sortBy:
    AdminContactInquirySortField

  sortDirection:
    AdminContactInquirySortDirection
}

export const defaultInquiryAdminFilters: InquiryAdminFilters =
  {
    search: "",

    inquiryType: "all",

    status: "all",

    priority: "all",

    readState: "all",

    assignment: "all",

    project: "all",

    createdFrom: "",
    createdTo: "",

    includeDeleted: false,

    sortBy: "created_at",

    sortDirection: "desc",
  }