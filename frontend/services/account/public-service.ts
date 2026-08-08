import {
  apiEndpoints,
  apiPost,
} from "@/lib/api"

import type {
  ForgotPasswordRequest,
  ForgotPasswordResponse,
  ResetPasswordRequest,
  ResetPasswordResponse,
} from "@/types/account"

export const publicAccountService = {
  forgotPassword(
    payload: ForgotPasswordRequest
  ): Promise<ForgotPasswordResponse> {
    return apiPost<
      ForgotPasswordResponse,
      ForgotPasswordRequest
    >(
      apiEndpoints.account.forgotPassword,
      payload
    )
  },

  resetPassword(
    payload: ResetPasswordRequest
  ): Promise<ResetPasswordResponse> {
    return apiPost<
      ResetPasswordResponse,
      ResetPasswordRequest
    >(
      apiEndpoints.account.resetPassword,
      payload
    )
  },
} as const