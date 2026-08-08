export type PermissionRead = {
  id: string
  created_at: string
  updated_at: string
  deleted_at: string | null

  code: string
  name: string
  description: string | null
  is_active: boolean
}

export type RoleRead = {
  id: string
  created_at: string
  updated_at: string
  deleted_at: string | null

  name: string
  display_name: string
  description: string | null
  is_system: boolean
  is_active: boolean

  permissions: PermissionRead[]
}

export type AuthenticatedUser = {
  id: string
  created_at: string
  updated_at: string
  deleted_at: string | null

  email: string
  first_name: string
  last_name: string
  display_name: string | null
  avatar_url: string | null

  is_active: boolean
  is_verified: boolean
  is_superuser: boolean

  roles: RoleRead[]
}

export type TokenPair = {
  access_token: string
  refresh_token: string
  token_type: string
  access_token_expires_at: string
  refresh_token_expires_at: string
}

export type BackendLoginRequest = {
  email: string
  password: string
  device_name?: string | null
}

export type BackendLoginResponse = {
  user: AuthenticatedUser
  tokens: TokenPair
}

export type BackendRefreshRequest = {
  refresh_token: string
}

export type BackendRefreshResponse = {
  user: AuthenticatedUser
  tokens: TokenPair
}

export type AdminLoginRequest = {
  email: string
  password: string
}

export type AdminSessionResponse = {
  user: AuthenticatedUser
}

export type AuthenticationErrorBody = {
  detail?: {
    code?: string
    message?: string
  }
  message?: string
}