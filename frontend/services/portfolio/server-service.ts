import "server-only"
import { apiEndpoints } from "@/lib/api"
import { serverApiGet } from "@/lib/api/server"

import type {
  ExperienceRead,
  ExperienceSummary,
  ProfileRead,
  ProjectCategoryRead,
  ProjectListResponse,
  ProjectRead,
  ProjectSummary,
  ProjectTechnologyCategory,
  ProjectTechnologyRead,
  PublicProjectListParams,
} from "@/types/portfolio"

export type PublicExperienceListParams = {
  page?: number
  page_size?: number
  search?: string
  employment_type?: string
  location_type?: string
  is_current?: boolean
  is_featured?: boolean
}

export type ExperienceListResponse = {
  items: ExperienceSummary[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
  has_next_page: boolean
  has_previous_page: boolean
}

function buildQueryString(
  params: Record<
    string,
    string | number | boolean | null | undefined
  >
): string {
  const searchParams = new URLSearchParams()

  for (const [key, value] of Object.entries(params)) {
    if (
      value === undefined ||
      value === null ||
      value === ""
    ) {
      continue
    }

    searchParams.set(
      key,
      String(value)
    )
  }

  const queryString =
    searchParams.toString()

  return queryString
    ? `?${queryString}`
    : ""
}

export const serverPortfolioService = {
  getProfile(): Promise<ProfileRead> {
    return serverApiGet<ProfileRead>(
      apiEndpoints.portfolio.profile
    )
  },

  getFeaturedProjects(
    limit = 6
  ): Promise<ProjectSummary[]> {
    return serverApiGet<ProjectSummary[]>(
      `${apiEndpoints.portfolio.featuredProjects}${buildQueryString({
        limit,
      })}`
    )
  },

  getProjects(
    params: PublicProjectListParams = {}
  ): Promise<ProjectListResponse> {
    return serverApiGet<ProjectListResponse>(
      `${apiEndpoints.portfolio.projects}${buildQueryString({
        page: params.page,
        page_size: params.page_size,
        search: params.search,
        category_slug: params.category_slug,
        technology_slug: params.technology_slug,
        is_featured: params.is_featured,
      })}`
    )
  },

  getProjectBySlug(
    slug: string
  ): Promise<ProjectRead> {
    return serverApiGet<ProjectRead>(
      apiEndpoints.portfolio.projectBySlug(
        slug
      )
    )
  },

  getCategories(): Promise<
    ProjectCategoryRead[]
  > {
    return serverApiGet<
      ProjectCategoryRead[]
    >(
      apiEndpoints.portfolio.categories
    )
  },

  getTechnologies(
    category?: ProjectTechnologyCategory
  ): Promise<ProjectTechnologyRead[]> {
    return serverApiGet<
      ProjectTechnologyRead[]
    >(
      `${apiEndpoints.portfolio.technologies}${buildQueryString({
        category,
      })}`
    )
  },

  getExperiences(
    params: PublicExperienceListParams = {}
  ): Promise<ExperienceListResponse> {
    return serverApiGet<ExperienceListResponse>(
      `${apiEndpoints.portfolio.experiences}${buildQueryString({
        page: params.page,
        page_size: params.page_size,
        search: params.search,
        employment_type: params.employment_type,
        location_type: params.location_type,
        is_current: params.is_current,
        is_featured: params.is_featured,
      })}`
    )
  },

  getExperienceBySlug(
    slug: string
  ): Promise<ExperienceRead> {
    return serverApiGet<ExperienceRead>(
      `${apiEndpoints.portfolio.experiences}/${encodeURIComponent(
        slug
      )}`
    )
  },

  getFeaturedExperiences(
    limit = 6
  ): Promise<ExperienceSummary[]> {
    return serverApiGet<
      ExperienceSummary[]
    >(
      `${apiEndpoints.portfolio.featuredExperiences}${buildQueryString({
        limit,
      })}`
    )
  },
} as const