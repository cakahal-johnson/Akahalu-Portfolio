import type {
  AdminProjectCategorySortDirection,
  AdminProjectCategorySortField,
} from "@/types/portfolio/project-category"

export type CategoryStatusFilter =
  | "all"
  | "active"
  | "inactive"

export type CategoryAdminFilterState = {
  search: string

  status:
    CategoryStatusFilter

  includeDeleted:
    boolean

  sortBy:
    AdminProjectCategorySortField

  sortDirection:
    AdminProjectCategorySortDirection
}

export const defaultCategoryAdminFilters:
  CategoryAdminFilterState = {
    search:
      "",

    status:
      "all",

    includeDeleted:
      false,

    sortBy:
      "sort_order",

    sortDirection:
      "asc",
  }