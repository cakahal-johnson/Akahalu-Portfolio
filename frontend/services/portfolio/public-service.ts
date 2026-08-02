import {
  apiEndpoints,
  apiGet,
} from "@/lib/api"

import type {
  ExperienceListResponse,
  ExperienceRead,
  ExperienceSummary,
  FeaturedExperienceParams,
  FeaturedProjectParams,
  ProfileRead,
  ProjectCategoryRead,
  ProjectListResponse,
  ProjectRead,
  ProjectSummary,
  ProjectTechnologyCategory,
  ProjectTechnologyRead,
  PublicExperienceListParams,
  PublicProjectListParams,
} from "@/types/portfolio"

export const publicPortfolioService = {
  getProfile(
    signal?: AbortSignal
  ): Promise<ProfileRead> {
    return apiGet<ProfileRead>(
      apiEndpoints.portfolio.profile,
      {
        signal,
      }
    )
  },

  getCategories(
    signal?: AbortSignal
  ): Promise<ProjectCategoryRead[]> {
    return apiGet<ProjectCategoryRead[]>(
      apiEndpoints.portfolio.categories,
      {
        signal,
      }
    )
  },

  getCategoryBySlug(
    slug: string,
    signal?: AbortSignal
  ): Promise<ProjectCategoryRead> {
    return apiGet<ProjectCategoryRead>(
      apiEndpoints.portfolio.categoryBySlug(slug),
      {
        signal,
      }
    )
  },

  getTechnologies(
    category?: ProjectTechnologyCategory,
    signal?: AbortSignal
  ): Promise<ProjectTechnologyRead[]> {
    return apiGet<ProjectTechnologyRead[]>(
      apiEndpoints.portfolio.technologies,
      {
        params: {
          category,
        },
        signal,
      }
    )
  },

  getTechnologyBySlug(
    slug: string,
    signal?: AbortSignal
  ): Promise<ProjectTechnologyRead> {
    return apiGet<ProjectTechnologyRead>(
      apiEndpoints.portfolio.technologyBySlug(slug),
      {
        signal,
      }
    )
  },

  getProjects(
    params: PublicProjectListParams = {},
    signal?: AbortSignal
  ): Promise<ProjectListResponse> {
    return apiGet<ProjectListResponse>(
      apiEndpoints.portfolio.projects,
      {
        params,
        signal,
      }
    )
  },

  getFeaturedProjects(
    params: FeaturedProjectParams = {},
    signal?: AbortSignal
  ): Promise<ProjectSummary[]> {
    return apiGet<ProjectSummary[]>(
      apiEndpoints.portfolio.featuredProjects,
      {
        params,
        signal,
      }
    )
  },

  getProjectBySlug(
    slug: string,
    signal?: AbortSignal
  ): Promise<ProjectRead> {
    return apiGet<ProjectRead>(
      apiEndpoints.portfolio.projectBySlug(slug),
      {
        signal,
      }
    )
  },

  getExperiences(
    params: PublicExperienceListParams = {},
    signal?: AbortSignal
  ): Promise<ExperienceListResponse> {
    return apiGet<ExperienceListResponse>(
      apiEndpoints.portfolio.experiences,
      {
        params,
        signal,
      }
    )
  },

  getFeaturedExperiences(
    params: FeaturedExperienceParams = {},
    signal?: AbortSignal
  ): Promise<ExperienceSummary[]> {
    return apiGet<ExperienceSummary[]>(
      apiEndpoints.portfolio.featuredExperiences,
      {
        params,
        signal,
      }
    )
  },

  getExperienceBySlug(
    slug: string,
    signal?: AbortSignal
  ): Promise<ExperienceRead> {
    return apiGet<ExperienceRead>(
      apiEndpoints.portfolio.experienceBySlug(slug),
      {
        signal,
      }
    )
  },
} as const