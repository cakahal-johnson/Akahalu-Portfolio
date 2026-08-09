import type {
  ProjectStatus,
  ProjectVisibility,
} from "@/types/portfolio/common"

import type {
  ProjectCategorySummary,
} from "@/types/portfolio/project-category"

import type {
  ProjectLinkRead,
} from "@/types/portfolio/project-link"

import type {
  ProjectMediaRead,
} from "@/types/portfolio/project-media"

import type {
  ProjectTechnologySummary,
} from "@/types/portfolio/project-technology"

import type {
  PaginatedApiResponse,
} from "@/types/api"

export type ProjectTechnologyAssignmentCreate = {
  technology_id: string

  is_featured?: boolean

  sort_order?: number
}

export type ProjectCreate = {
  title: string
  slug: string

  short_description: string
  description: string

  problem_statement?: string | null
  solution_summary?: string | null
  key_features?: string | null
  technical_highlights?: string | null

  category_id?: string | null

  status?: ProjectStatus
  visibility?: ProjectVisibility

  is_featured?: boolean
  sort_order?: number

  repository_url?: string | null
  live_url?: string | null
  case_study_url?: string | null
  thumbnail_url?: string | null

  started_at?: string | null
  completed_at?: string | null
  published_at?: string | null

  seo_title?: string | null
  seo_description?: string | null

  technology_assignments?:
    ProjectTechnologyAssignmentCreate[]
}

export type ProjectUpdate = {
  title?: string
  slug?: string

  short_description?: string
  description?: string

  problem_statement?: string | null
  solution_summary?: string | null
  key_features?: string | null
  technical_highlights?: string | null

  category_id?: string | null

  status?: ProjectStatus
  visibility?: ProjectVisibility

  is_featured?: boolean
  sort_order?: number

  repository_url?: string | null
  live_url?: string | null
  case_study_url?: string | null
  thumbnail_url?: string | null

  started_at?: string | null
  completed_at?: string | null
  published_at?: string | null

  seo_title?: string | null
  seo_description?: string | null

  technology_assignments?:
    ProjectTechnologyAssignmentCreate[]
}

export type ProjectSummary = {
  id: string

  title: string
  slug: string

  short_description: string

  status: ProjectStatus
  visibility: ProjectVisibility

  is_featured: boolean
  sort_order: number

  thumbnail_url: string | null

  started_at: string | null
  completed_at: string | null
  published_at: string | null

  category: ProjectCategorySummary | null

  technologies: ProjectTechnologySummary[]
}

export type ProjectRead =
  ProjectSummary & {
    description: string

    problem_statement: string | null
    solution_summary: string | null
    key_features: string | null
    technical_highlights: string | null

    repository_url: string | null
    live_url: string | null
    case_study_url: string | null

    seo_title: string | null
    seo_description: string | null

    media: ProjectMediaRead[]
    links: ProjectLinkRead[]
  }

export type ProjectTechnologyAssignmentRead = {
  technology: ProjectTechnologySummary

  is_featured: boolean

  sort_order: number
}

export type ProjectAdminRead = {
  id: string

  title: string
  slug: string

  short_description: string
  description: string

  problem_statement: string | null
  solution_summary: string | null
  key_features: string | null
  technical_highlights: string | null

  category_id: string | null

  status: ProjectStatus
  visibility: ProjectVisibility

  is_featured: boolean
  sort_order: number

  repository_url: string | null
  live_url: string | null
  case_study_url: string | null
  thumbnail_url: string | null

  started_at: string | null
  completed_at: string | null
  published_at: string | null

  seo_title: string | null
  seo_description: string | null

  created_at: string
  updated_at: string
  deleted_at: string | null

  created_by_id: string | null
  updated_by_id: string | null

  category: ProjectCategorySummary | null

  technology_assignments:
    ProjectTechnologyAssignmentRead[]

  media: ProjectMediaRead[]
  links: ProjectLinkRead[]
}

export type ProjectListResponse =
  PaginatedApiResponse<ProjectSummary>

export type AdminProjectListResponse =
  PaginatedApiResponse<ProjectAdminRead>

export type PublicProjectListParams = {
  page?: number
  page_size?: number

  search?: string

  category_slug?: string
  technology_slug?: string

  is_featured?: boolean
}

export type FeaturedProjectParams = {
  limit?: number
}

export type AdminProjectSortField =
  | "title"
  | "slug"
  | "status"
  | "visibility"
  | "is_featured"
  | "sort_order"
  | "started_at"
  | "completed_at"
  | "published_at"
  | "created_at"
  | "updated_at"

export type AdminProjectSortDirection =
  | "asc"
  | "desc"

export type AdminProjectListParams = {
  page?: number
  page_size?: number

  search?: string

  category_id?: string
  technology_id?: string

  project_status?: ProjectStatus
  visibility?: ProjectVisibility

  is_featured?: boolean

  include_deleted?: boolean

  sort_by?: AdminProjectSortField
  sort_direction?: AdminProjectSortDirection
}

export type ProjectStatusUpdate = {
  status: ProjectStatus

  published_at?: string | null

  reason?: string | null
}

export type ProjectVisibilityUpdate = {
  visibility: ProjectVisibility

  reason?: string | null
}

export type ProjectFeaturedUpdate = {
  is_featured: boolean

  reason?: string | null
}