export type ForgotPasswordRequest = {
  email: string
}

export type ForgotPasswordResponse = {
  message: string
  reset_token: string | null
  reset_token_expires_at: string | null
}

export type ResetPasswordRequest = {
  token: string
  new_password: string
}

export type ResetPasswordResponse = {
  message: string
}