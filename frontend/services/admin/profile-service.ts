import {
  adminRequest,
} from "@/services/admin/client"

import type {
  ProfileAdminRead,
  ProfileAdminUpdate,
  ProfileVisibilityUpdate,
} from "@/types/portfolio/profile"

const PROFILE_ENDPOINT =
  "/api/admin/profile"

export const adminProfileService =
  {
    getProfile(): Promise<ProfileAdminRead> {
      return adminRequest<ProfileAdminRead>(
        PROFILE_ENDPOINT
      )
    },

    updateProfile(
      payload: ProfileAdminUpdate
    ): Promise<ProfileAdminRead> {
      return adminRequest<ProfileAdminRead>(
        PROFILE_ENDPOINT,
        {
          method: "PATCH",
          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },

    updateVisibility(
      payload: ProfileVisibilityUpdate
    ): Promise<ProfileAdminRead> {
      return adminRequest<ProfileAdminRead>(
        `${PROFILE_ENDPOINT}/visibility`,
        {
          method: "PATCH",
          body:
            JSON.stringify(
              payload
            ),
        }
      )
    },
  } as const