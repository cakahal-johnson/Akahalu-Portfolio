export type ProjectStatus =
  | "draft"
  | "published"
  | "archived"

export type ProjectVisibility =
  | "public"
  | "private"
  | "unlisted"

export type ProjectTechnologyCategory =
  | "language"
  | "framework"
  | "library"
  | "database"
  | "platform"
  | "cloud"
  | "devops"
  | "testing"
  | "tool"
  | "service"
  | "other"

export type ProjectLinkType =
  | "repository"
  | "live_demo"
  | "documentation"
  | "case_study"
  | "video"
  | "download"
  | "app_store"
  | "play_store"
  | "design"
  | "article"
  | "api"
  | "other"

export type ProjectMediaType =
  | "image"
  | "video"
  | "document"
  | "demo"
  | "other"

export type SortDirection =
  | "asc"
  | "desc"

export type ProjectSortField =
  | "created_at"
  | "updated_at"
  | "published_at"
  | "title"
  | "sort_order"