import {
  queryOptions,
} from "@tanstack/react-query"

import { queryKeys } from "@/lib/query/keys"
import {
  publicPortfolioService,
} from "@/services/portfolio"

import type {
  ProjectTechnologyCategory,
  PublicExperienceListParams,
  PublicProjectListParams,
} from "@/types/portfolio"

export function profileQueryOptions() {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.profile(),

    queryFn: ({ signal }) =>
      publicPortfolioService.getProfile(
        signal
      ),
  })
}

export function categoriesQueryOptions() {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.categories(),

    queryFn: ({ signal }) =>
      publicPortfolioService.getCategories(
        signal
      ),
  })
}

export function technologiesQueryOptions(
  category?: ProjectTechnologyCategory
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.technologies(
        category
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getTechnologies(
        category,
        signal
      ),
  })
}

export function projectsQueryOptions(
  params: PublicProjectListParams = {}
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.projects(
        params
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getProjects(
        params,
        signal
      ),
  })
}

export function featuredProjectsQueryOptions(
  limit = 6
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.featuredProjects(
        limit
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getFeaturedProjects(
        {
          limit,
        },
        signal
      ),
  })
}

export function projectQueryOptions(
  slug: string
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.project(slug),

    queryFn: ({ signal }) =>
      publicPortfolioService.getProjectBySlug(
        slug,
        signal
      ),
  })
}

export function experiencesQueryOptions(
  params: PublicExperienceListParams = {}
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.experiences(
        params
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getExperiences(
        params,
        signal
      ),
  })
}

export function featuredExperiencesQueryOptions(
  limit = 6
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.featuredExperiences(
        limit
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getFeaturedExperiences(
        {
          limit,
        },
        signal
      ),
  })
}

export function experienceQueryOptions(
  slug: string
) {
  return queryOptions({
    queryKey:
      queryKeys.portfolio.experience(
        slug
      ),

    queryFn: ({ signal }) =>
      publicPortfolioService.getExperienceBySlug(
        slug,
        signal
      ),
  })
}