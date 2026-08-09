import type {
  AdminUserSortDirection,
  AdminUserSortField,
  AdminUserStatus,
} from "@/types/admin-user"

export type AdminUserBooleanFilter =
  | "all"
  | "yes"
  | "no"

export type AdminUserStatusFilter =
  | "all"
  | AdminUserStatus

export type AdminUserFilterState = {
  search: string

  status:
    AdminUserStatusFilter

  verified:
    AdminUserBooleanFilter

  superuser:
    AdminUserBooleanFilter

  includeDeleted:
    boolean

  sortBy:
    AdminUserSortField

  sortDirection:
    AdminUserSortDirection
}

export const defaultAdminUserFilters:
  AdminUserFilterState = {
    search:
      "",

    status:
      "all",

    verified:
      "all",

    superuser:
      "all",

    includeDeleted:
      false,

    sortBy:
      "created_at",

    sortDirection:
      "desc",
  }