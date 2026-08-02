import type {
  ProjectLinkType,
} from "@/types/portfolio/common"

export type ProjectLinkRead = {
  id: string
  project_id: string

  label: string
  url: string

  link_type: ProjectLinkType

  icon: string | null

  opens_in_new_tab: boolean

  sort_order: number
}