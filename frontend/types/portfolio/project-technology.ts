import type {
  PaginatedApiResponse,
} from "@/types/api"

import type {
  ProjectTechnologyCategory,
} from "@/types/portfolio/common"

export type ProjectTechnologySummary = {
  id: string

  name: string
  slug: string

  category:
    ProjectTechnologyCategory

  icon: string | null
  official_url: string | null
  color: string | null

  sort_order: number
}

export type ProjectTechnologyRead =
  ProjectTechnologySummary & {
    description:
      string | null
  }

export type ProjectTechnologyAdminRead = {
  id: string

  name: string
  slug: string

  description:
    string | null

  category:
    ProjectTechnologyCategory

  icon: string | null
  official_url: string | null
  color: string | null

  is_active: boolean

  sort_order: number

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ProjectTechnologyCreate = {
  name: string
  slug: string

  description?:
    string | null

  category?:
    ProjectTechnologyCategory

  icon?:
    string | null

  official_url?:
    string | null

  color?:
    string | null

  is_active?: boolean

  sort_order?: number
}

export type ProjectTechnologyUpdate = {
  name?: string
  slug?: string

  description?:
    string | null

  category?:
    ProjectTechnologyCategory

  icon?:
    string | null

  official_url?:
    string | null

  color?:
    string | null

  is_active?: boolean

  sort_order?: number
}

export type ProjectTechnologyStatusUpdate = {
  is_active: boolean

  reason?:
    string | null
}

export type ProjectTechnologyDeleteRequest = {
  reason?:
    string | null
}

export type ProjectTechnologyRestoreRequest = {
  activate?: boolean

  reason?:
    string | null
}

export type AdminProjectTechnologySortField =
  | "sort_order"
  | "name"
  | "slug"
  | "category"
  | "created_at"
  | "updated_at"

export type AdminProjectTechnologySortDirection =
  | "asc"
  | "desc"

export type AdminProjectTechnologyListParams = {
  page?: number
  page_size?: number

  search?: string

  category?:
    ProjectTechnologyCategory

  is_active?: boolean

  include_deleted?: boolean

  sort_by?:
    AdminProjectTechnologySortField

  sort_direction?:
    AdminProjectTechnologySortDirection
}

export type AdminProjectTechnologyListResponse =
  PaginatedApiResponse<ProjectTechnologyAdminRead>