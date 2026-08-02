import type {
  ProjectMediaType,
} from "@/types/portfolio/common"

export type ProjectMediaRead = {
  id: string
  project_id: string

  media_type: ProjectMediaType

  url: string
  thumbnail_url: string | null

  alt_text: string | null
  caption: string | null

  provider: string | null
  provider_asset_id: string | null

  mime_type: string | null

  width: number | null
  height: number | null

  file_size_bytes: number | null
  duration_seconds: number | null

  is_primary: boolean
  sort_order: number

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ProjectMediaSummary = {
  id: string
  project_id: string

  media_type: ProjectMediaType

  url: string
  thumbnail_url: string | null

  alt_text: string | null
  caption: string | null

  width: number | null
  height: number | null

  duration_seconds: number | null

  is_primary: boolean
  sort_order: number
}