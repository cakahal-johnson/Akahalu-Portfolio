import type {
  PaginatedApiResponse,
} from "@/types/api"

export type EmploymentType =
  | "full_time"
  | "part_time"
  | "contract"
  | "freelance"
  | "internship"
  | "apprenticeship"
  | "temporary"
  | "volunteer"
  | "self_employed"
  | "other"

export type ExperienceLocationType =
  | "onsite"
  | "remote"
  | "hybrid"

export type ExperienceSummary = {
  id: string

  company_name: string
  job_title: string
  slug: string

  employment_type:
    EmploymentType

  location: string | null

  location_type:
    ExperienceLocationType

  start_date: string
  end_date: string | null

  is_current: boolean

  summary: string

  company_website:
    string | null

  company_logo_url:
    string | null

  sort_order: number

  is_featured: boolean
}

export type ExperienceRead =
  ExperienceSummary & {
    responsibilities:
      string | null

    achievements:
      string | null
  }

export type ExperienceAdminRead = {
  id: string

  company_name: string
  job_title: string
  slug: string

  employment_type:
    EmploymentType

  location:
    string | null

  location_type:
    ExperienceLocationType

  start_date: string
  end_date: string | null

  is_current: boolean

  summary: string

  responsibilities:
    string | null

  achievements:
    string | null

  company_website:
    string | null

  company_logo_url:
    string | null

  sort_order: number

  is_featured: boolean
  is_public: boolean

  created_by_id:
    string | null

  updated_by_id:
    string | null

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ExperienceCreate = {
  company_name: string
  job_title: string
  slug: string

  employment_type?:
    EmploymentType

  location?:
    string | null

  location_type?:
    ExperienceLocationType

  start_date: string

  end_date?:
    string | null

  is_current?: boolean

  summary: string

  responsibilities?:
    string | null

  achievements?:
    string | null

  company_website?:
    string | null

  company_logo_url?:
    string | null

  sort_order?: number

  is_featured?: boolean
  is_public?: boolean
}

export type ExperienceUpdate = {
  company_name?: string
  job_title?: string
  slug?: string

  employment_type?:
    EmploymentType

  location?:
    string | null

  location_type?:
    ExperienceLocationType

  start_date?: string

  end_date?:
    string | null

  is_current?: boolean

  summary?:
    string | null

  responsibilities?:
    string | null

  achievements?:
    string | null

  company_website?:
    string | null

  company_logo_url?:
    string | null

  sort_order?: number

  is_featured?: boolean
  is_public?: boolean
}

export type ExperienceVisibilityUpdate = {
  is_public: boolean

  reason?:
    string | null
}

export type ExperienceFeaturedUpdate = {
  is_featured: boolean

  reason?:
    string | null
}

export type ExperienceDeleteRequest = {
  reason?:
    string | null
}

export type ExperienceRestoreRequest = {
  make_public?: boolean

  reason?:
    string | null
}

export type AdminExperienceSortField =
  | "company_name"
  | "job_title"
  | "slug"
  | "employment_type"
  | "location_type"
  | "start_date"
  | "end_date"
  | "is_current"
  | "is_public"
  | "is_featured"
  | "sort_order"
  | "created_at"
  | "updated_at"

export type AdminExperienceSortDirection =
  | "asc"
  | "desc"

export type AdminExperienceListParams = {
  page?: number
  page_size?: number

  search?: string

  employment_type?:
    EmploymentType

  location_type?:
    ExperienceLocationType

  is_current?: boolean
  is_public?: boolean
  is_featured?: boolean

  include_deleted?: boolean

  sort_by?:
    AdminExperienceSortField

  sort_direction?:
    AdminExperienceSortDirection
}

export type ExperienceListResponse =
  PaginatedApiResponse<ExperienceSummary>

export type AdminExperienceListResponse =
  PaginatedApiResponse<ExperienceAdminRead>

export type PublicExperienceListParams = {
  page?: number
  page_size?: number

  search?: string

  employment_type?:
    EmploymentType

  location_type?:
    ExperienceLocationType

  is_current?: boolean
  is_featured?: boolean
}

export type FeaturedExperienceParams = {
  limit?: number
}