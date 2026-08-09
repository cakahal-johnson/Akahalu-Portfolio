import type {
  ProjectTechnologyCategory,
} from "@/types/portfolio/common"

import type {
  AdminProjectTechnologySortDirection,
  AdminProjectTechnologySortField,
} from "@/types/portfolio/project-technology"

export type TechnologyStatusFilter =
  | "all"
  | "active"
  | "inactive"

export type TechnologyCategoryFilter =
  | "all"
  | ProjectTechnologyCategory

export type TechnologyAdminFilterState = {
  search: string

  category:
    TechnologyCategoryFilter

  status:
    TechnologyStatusFilter

  includeDeleted:
    boolean

  sortBy:
    AdminProjectTechnologySortField

  sortDirection:
    AdminProjectTechnologySortDirection
}

export const defaultTechnologyAdminFilters:
  TechnologyAdminFilterState = {
    search:
      "",

    category:
      "all",

    status:
      "all",

    includeDeleted:
      false,

    sortBy:
      "sort_order",

    sortDirection:
      "asc",
  }