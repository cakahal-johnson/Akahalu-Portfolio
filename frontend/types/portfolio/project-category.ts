import type {
  PaginatedApiResponse,
} from "@/types/api"

export type ProjectCategorySummary = {
  id: string

  name: string
  slug: string

  description: string | null
  icon: string | null
  color: string | null

  sort_order: number
}

export type ProjectCategoryRead =
  ProjectCategorySummary & {
    seo_title: string | null
    seo_description: string | null
  }

export type ProjectCategoryAdminRead = {
  id: string

  name: string
  slug: string

  description: string | null
  icon: string | null
  color: string | null

  is_active: boolean

  sort_order: number

  seo_title: string | null
  seo_description: string | null

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ProjectCategoryCreate = {
  name: string
  slug: string

  description?: string | null
  icon?: string | null
  color?: string | null

  is_active?: boolean

  sort_order?: number

  seo_title?: string | null
  seo_description?: string | null
}

export type ProjectCategoryUpdate = {
  name?: string
  slug?: string

  description?: string | null
  icon?: string | null
  color?: string | null

  is_active?: boolean

  sort_order?: number

  seo_title?: string | null
  seo_description?: string | null
}

export type ProjectCategoryStatusUpdate = {
  is_active: boolean

  reason?: string | null
}

export type ProjectCategoryDeleteRequest = {
  reason?: string | null
}

export type ProjectCategoryRestoreRequest = {
  activate?: boolean

  reason?: string | null
}

export type AdminProjectCategorySortField =
  | "sort_order"
  | "name"
  | "slug"
  | "created_at"
  | "updated_at"

export type AdminProjectCategorySortDirection =
  | "asc"
  | "desc"

export type AdminProjectCategoryListParams = {
  page?: number
  page_size?: number

  search?: string

  is_active?: boolean

  include_deleted?: boolean

  sort_by?: AdminProjectCategorySortField
  sort_direction?: AdminProjectCategorySortDirection
}

export type AdminProjectCategoryListResponse =
  PaginatedApiResponse<ProjectCategoryAdminRead>