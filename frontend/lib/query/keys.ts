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

    projects: () =>
      ["portfolio", "projects"] as const,

    project: (slug: string) =>
      ["portfolio", "projects", slug] as const,

    categories: () =>
      ["portfolio", "categories"] as const,

    technologies: () =>
      ["portfolio", "technologies"] as const,

    technology: (slug: string) =>
      ["portfolio", "technologies", slug] as const,

    experiences: () =>
      ["portfolio", "experiences"] as const,
  },
} as const