import type {
  RoleRead,
} from "@/types/authentication"

export type AdminUserStatus =
  | "active"
  | "inactive"

export type AdminUserSortField =
  | "created_at"
  | "email"
  | "first_name"
  | "last_name"
  | "display_name"

export type AdminUserSortDirection =
  | "asc"
  | "desc"

export type AdminUserListParams = {
  page?: number
  page_size?: number
  search?: string

  status?:
    AdminUserStatus

  is_verified?:
    boolean

  is_superuser?:
    boolean

  include_deleted?:
    boolean

  sort_by?:
    AdminUserSortField

  sort_direction?:
    AdminUserSortDirection
}

export type AdminUserSummary = {
  id: string
  email: string

  first_name: string
  last_name: string

  display_name:
    string | null

  avatar_url:
    string | null

  is_active: boolean
  is_verified: boolean
  is_superuser: boolean
  is_deleted: boolean

  created_at: string
  updated_at: string

  deleted_at:
    string | null

  roles:
    RoleRead[]
}

export type AdminUserDetail =
  AdminUserSummary & {
    last_login_at:
      string | null
  }

export type AdminUserListResponse = {
  items:
    AdminUserSummary[]

  page: number
  page_size: number

  total_items: number
  total_pages: number

  has_next_page:
    boolean

  has_previous_page:
    boolean
}

export type AdminUserStatusUpdate = {
  is_active: boolean

  reason?:
    string | null
}

export type AdminUserDeleteRequest = {
  reason?:
    string | null
}

export type AdminUserRestoreRequest = {
  activate?: boolean

  reason?:
    string | null
}