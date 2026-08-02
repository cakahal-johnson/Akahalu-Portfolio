import type {
  ProjectTechnologyCategory,
  PublicExperienceListParams,
  PublicProjectListParams,
} from "@/types/portfolio"

export const queryKeys = {
  health: {
    all: ["health"] as const,

    live: ["health", "live"] as const,

    ready: ["health", "ready"] as const,
  },

  portfolio: {
    all: ["portfolio"] as const,

    profile: () =>
      ["portfolio", "profile"] as const,

    categories: () =>
      ["portfolio", "categories"] as const,

    category: (slug: string) =>
      [
        "portfolio",
        "categories",
        slug,
      ] as const,

    technologies: (
      category?: ProjectTechnologyCategory
    ) =>
      [
        "portfolio",
        "technologies",
        {
          category: category ?? null,
        },
      ] as const,

    technology: (slug: string) =>
      [
        "portfolio",
        "technologies",
        slug,
      ] as const,

    projects: (
      params: PublicProjectListParams = {}
    ) =>
      [
        "portfolio",
        "projects",
        params,
      ] as const,

    featuredProjects: (limit = 6) =>
      [
        "portfolio",
        "projects",
        "featured",
        {
          limit,
        },
      ] as const,

    project: (slug: string) =>
      [
        "portfolio",
        "projects",
        slug,
      ] as const,

    experiences: (
      params: PublicExperienceListParams = {}
    ) =>
      [
        "portfolio",
        "experiences",
        params,
      ] as const,

    featuredExperiences: (limit = 6) =>
      [
        "portfolio",
        "experiences",
        "featured",
        {
          limit,
        },
      ] as const,

    experience: (slug: string) =>
      [
        "portfolio",
        "experiences",
        slug,
      ] as const,
  },
} as const