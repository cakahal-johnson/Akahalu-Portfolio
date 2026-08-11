import { ApiError } from "@/lib/api"

import {
  serverPortfolioService,
} from "@/services/portfolio/server-service"

import type {
  ProfileRead,
} from "@/types/portfolio"

export async function getPublicProfile(): Promise<
  ProfileRead | null
> {
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
      "[portfolio] Public profile is unavailable; using the unavailable-profile fallback."
    )

    return null
  }
}