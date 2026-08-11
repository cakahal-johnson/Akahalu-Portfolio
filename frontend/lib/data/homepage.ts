import { ApiError } from "@/lib/api"
import {
  serverPortfolioService,
} from "@/services/portfolio/server-service"

import type {
  ExperienceSummary,
  ProfileRead,
  ProjectSummary,
} from "@/types/portfolio"

export type HomepageData = {
  profile: ProfileRead | null
  featuredProjects: ProjectSummary[]
  featuredExperiences: ExperienceSummary[]
}

async function loadProfile(): Promise<ProfileRead | null> {
  try {
    return await serverPortfolioService.getProfile()
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === 404
    ) {
      return null
    }

    console.warn(
      "[portfolio] Public profile is unavailable; using homepage fallback content."
    )

    return null
  }
}

async function loadFeaturedProjects(): Promise<
  ProjectSummary[]
> {
  try {
    return await serverPortfolioService.getFeaturedProjects(
      3
    )
  } catch {
    return []
  }
}

async function loadFeaturedExperiences(): Promise<
  ExperienceSummary[]
> {
  try {
    return await serverPortfolioService.getFeaturedExperiences(
      3
    )
  } catch {
    return []
  }
}

export async function getHomepageData(): Promise<HomepageData> {
  const [
    profile,
    featuredProjects,
    featuredExperiences,
  ] = await Promise.all([
    loadProfile(),
    loadFeaturedProjects(),
    loadFeaturedExperiences(),
  ])

  return {
    profile,
    featuredProjects,
    featuredExperiences,
  }
}