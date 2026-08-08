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

  account: {
    register: "/account/register",
    verifyEmail: "/account/verify-email",
    resendVerification: "/account/resend-verification",
    forgotPassword: "/account/forgot-password",
    resetPassword: "/account/reset-password",
  },

  portfolio: {
    profile: "/portfolio/profile",
    categories: "/portfolio/categories",

    categoryBySlug: (slug: string) =>
      `/portfolio/categories/${encodeURIComponent(slug)}`,

    technologies: "/portfolio/technologies",

    technologyBySlug: (slug: string) =>
      `/portfolio/technologies/${encodeURIComponent(slug)}`,

    projects: "/portfolio/projects",

    featuredProjects:
      "/portfolio/projects/featured",

    projectBySlug: (slug: string) =>
      `/portfolio/projects/${encodeURIComponent(slug)}`,

    experiences:
      "/portfolio/experiences",

    featuredExperiences:
      "/portfolio/experiences/featured",

    experienceBySlug: (slug: string) =>
      `/portfolio/experiences/${encodeURIComponent(slug)}`,
  },

  contact: {
    inquiries: "/contact/inquiries",
  },
} as const