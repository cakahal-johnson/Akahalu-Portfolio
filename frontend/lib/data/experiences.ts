import {
  serverPortfolioService,
  type ExperienceListResponse,
  type PublicExperienceListParams,
} from "@/services/portfolio/server-service"

function createEmptyExperienceList(
  params: PublicExperienceListParams
): ExperienceListResponse {
  const page =
    params.page && params.page > 0
      ? params.page
      : 1

  const pageSize =
    params.page_size &&
    params.page_size > 0
      ? params.page_size
      : 12

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

export async function getExperienceDirectoryData(
  params: PublicExperienceListParams
): Promise<ExperienceListResponse> {
  try {
    return await serverPortfolioService.getExperiences(
      params
    )
  } catch {
    return createEmptyExperienceList(
      params
    )
  }
}