import { ApiError } from "@/lib/api"
import { serverPortfolioService } from "@/services/portfolio"

import type { ProfileRead } from "@/types/portfolio"

export async function getPublicProfile(): Promise<ProfileRead | null> {
  try {
    return await serverPortfolioService.getProfile()
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