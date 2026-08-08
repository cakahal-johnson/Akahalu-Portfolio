import type {
  AdminProjectSortDirection,
  AdminProjectSortField,
} from "@/types/portfolio/project"

import type {
  ProjectStatus,
  ProjectVisibility,
} from "@/types/portfolio/common"

export type ProjectAdminFilterState = {
  search: string

  categoryId: string
  technologyId: string

  status:
    | ProjectStatus
    | ""

  visibility:
    | ProjectVisibility
    | ""

  featured:
    | "all"
    | "true"
    | "false"

  includeDeleted: boolean

  sortBy:
    AdminProjectSortField

  sortDirection:
    AdminProjectSortDirection
}

export const defaultProjectAdminFilters: ProjectAdminFilterState =
  {
    search: "",

    categoryId: "",
    technologyId: "",

    status: "",
    visibility: "",

    featured: "all",

    includeDeleted: false,

    sortBy: "created_at",
    sortDirection: "desc",
  }