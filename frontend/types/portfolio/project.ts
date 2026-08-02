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

export type ProjectListResponse =
  PaginatedApiResponse<ProjectSummary>

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