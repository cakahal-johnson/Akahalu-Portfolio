export const apiEndpoints = {
  health: {
    live: "/live",
    ready: "/ready",
    health: "/health",
  },

  authentication: {
    login: "/auth/login",
    refresh: "/auth/refresh",
    logout: "/auth/logout",
    me: "/auth/me",
  },

  portfolio: {
    profile: "/portfolio/profile",
    projects: "/portfolio/projects",
    categories: "/portfolio/categories",
    technologies: "/portfolio/technologies",
    experiences: "/portfolio/experiences",

    projectBySlug: (slug: string) =>
      `/portfolio/projects/${encodeURIComponent(slug)}`,

    technologyBySlug: (slug: string) =>
      `/portfolio/technologies/${encodeURIComponent(slug)}`,
  },

  contact: {
    inquiries: "/contact/inquiries",
  },
} as const