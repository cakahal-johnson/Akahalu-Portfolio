export type ProfileAvailabilityStatus =
  | "available"
  | "open_to_opportunities"
  | "limited_availability"
  | "unavailable"

export type ProfileRead = {
  id: string

  first_name: string
  middle_name: string | null
  last_name: string

  display_name: string

  professional_title: string
  headline: string

  short_bio: string
  biography: string

  location: string | null
  country: string | null
  timezone: string | null

  primary_email: string
  phone: string | null

  website_url: string | null
  resume_url: string | null
  profile_image_url: string | null

  years_of_experience: number

  availability_status: ProfileAvailabilityStatus
  availability_message: string | null

  is_public: boolean

  seo_title: string | null
  seo_description: string | null

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ProfileAdminRead =
  ProfileRead & {
    profile_key: string
    created_by_id: string | null
    updated_by_id: string | null
  }

export type ProfileAdminUpdate = {
  first_name: string
  middle_name: string | null
  last_name: string

  display_name: string

  professional_title: string
  headline: string

  short_bio: string
  biography: string

  location: string | null
  country: string | null
  timezone: string | null

  primary_email: string
  phone: string | null

  website_url: string | null
  resume_url: string | null
  profile_image_url: string | null

  years_of_experience: number

  availability_status: ProfileAvailabilityStatus
  availability_message: string | null

  seo_title: string | null
  seo_description: string | null
}

export type ProfileVisibilityUpdate = {
  is_public: boolean
  reason?: string | null
}