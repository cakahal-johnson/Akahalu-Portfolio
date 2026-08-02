import { apiEndpoints } from "@/lib/api"
import { serverApiGet } from "@/lib/api/server"

import type {
  ExperienceSummary,
  ProfileRead,
  ProjectSummary,
} from "@/types/portfolio"

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
      `${apiEndpoints.portfolio.featuredProjects}?limit=${limit}`
    )
  },

  getFeaturedExperiences(
    limit = 6
  ): Promise<ExperienceSummary[]> {
    return serverApiGet<ExperienceSummary[]>(
      `${apiEndpoints.portfolio.featuredExperiences}?limit=${limit}`
    )
  },
} as const