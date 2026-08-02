import type {
  ProjectTechnologyCategory,
} from "@/types/portfolio/common"

export type ProjectTechnologySummary = {
  id: string

  name: string
  slug: string

  category: ProjectTechnologyCategory

  icon: string | null
  official_url: string | null
  color: string | null

  sort_order: number
}

export type ProjectTechnologyRead =
  ProjectTechnologySummary & {
    description: string | null
  }