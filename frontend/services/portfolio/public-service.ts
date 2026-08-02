import {
  apiEndpoints,
  apiGet,
} from "@/lib/api"

export const publicPortfolioService = {
  getProfile<TResponse>(
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.profile,
      {
        signal,
      }
    )
  },

  getProjects<TResponse>(
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.projects,
      {
        signal,
      }
    )
  },

  getProjectBySlug<TResponse>(
    slug: string,
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.projectBySlug(slug),
      {
        signal,
      }
    )
  },

  getCategories<TResponse>(
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.categories,
      {
        signal,
      }
    )
  },

  getTechnologies<TResponse>(
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.technologies,
      {
        signal,
      }
    )
  },

  getTechnologyBySlug<TResponse>(
    slug: string,
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.technologyBySlug(slug),
      {
        signal,
      }
    )
  },

  getExperiences<TResponse>(
    signal?: AbortSignal
  ): Promise<TResponse> {
    return apiGet<TResponse>(
      apiEndpoints.portfolio.experiences,
      {
        signal,
      }
    )
  },
} as const