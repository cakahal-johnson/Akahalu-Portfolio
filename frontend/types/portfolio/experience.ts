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

  employment_type: EmploymentType

  location: string | null
  location_type: ExperienceLocationType

  start_date: string
  end_date: string | null

  is_current: boolean

  summary: string

  company_website: string | null
  company_logo_url: string | null

  sort_order: number
  is_featured: boolean
}

export type ExperienceRead =
  ExperienceSummary & {
    responsibilities: string | null
    achievements: string | null
  }

export type ExperienceListResponse =
  PaginatedApiResponse<ExperienceSummary>

export type PublicExperienceListParams = {
  page?: number
  page_size?: number

  search?: string

  employment_type?: EmploymentType

  location_type?: ExperienceLocationType

  is_current?: boolean
  is_featured?: boolean
}

export type FeaturedExperienceParams = {
  limit?: number
}