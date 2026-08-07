import { apiEndpoints } from "@/lib/api"
import { serverApiGet } from "@/lib/api/server"

import type {
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