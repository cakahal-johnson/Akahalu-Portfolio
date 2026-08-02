export type ProjectCategorySummary = {
  id: string

  name: string
  slug: string

  description: string | null
  icon: string | null
  color: string | null

  sort_order: number
}

export type ProjectCategoryRead =
  ProjectCategorySummary & {
    seo_title: string | null
    seo_description: string | null
  }