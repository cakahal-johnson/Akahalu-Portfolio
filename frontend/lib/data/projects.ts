import { ApiError } from "@/lib/api"
import {
  serverPortfolioService,
} from "@/services/portfolio/server-service"

import type {
  ProjectCategoryRead,
  ProjectListResponse,
  ProjectRead,
  ProjectTechnologyRead,
  PublicProjectListParams,
} from "@/types/portfolio"

export type ProjectDirectoryData = {
  projects: ProjectListResponse
  categories: ProjectCategoryRead[]
  technologies: ProjectTechnologyRead[]
}

function createEmptyProjectList(
  params: PublicProjectListParams
): ProjectListResponse {
  const page =
    params.page && params.page > 0
      ? params.page
      : 1

  const pageSize =
    params.page_size &&
    params.page_size > 0
      ? params.page_size
      : 9

  return {
    items: [],
    page,
    page_size: pageSize,
    total_items: 0,
    total_pages: 0,
    has_next_page: false,
    has_previous_page: false,
  }
}

export async function getProjectDirectoryData(
  params: PublicProjectListParams
): Promise<ProjectDirectoryData> {
  const [
    projectsResult,
    categoriesResult,
    technologiesResult,
  ] = await Promise.allSettled([
    serverPortfolioService.getProjects(
      params
    ),

    serverPortfolioService.getCategories(),

    serverPortfolioService.getTechnologies(),
  ])

  const projects =
    projectsResult.status === "fulfilled"
      ? projectsResult.value
      : createEmptyProjectList(params)

  const categories =
    categoriesResult.status === "fulfilled"
      ? categoriesResult.value
      : []

  const technologies =
    technologiesResult.status === "fulfilled"
      ? technologiesResult.value
      : []

  return {
    projects,
    categories,
    technologies,
  }
}

export async function getPublicProject(
  slug: string
): Promise<ProjectRead | null> {
  try {
    return await serverPortfolioService.getProjectBySlug(
      slug
    )
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status === 404
    ) {
      return null
    }

    throw error
  }
}