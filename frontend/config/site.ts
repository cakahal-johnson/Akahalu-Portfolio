import { env } from "@/config/env"

export const siteConfig = {
  name: "Akahalu Vitalis",
  shortName: "Akahalu",
  initials: "AV",

  title: "Akahalu Vitalis | Full-Stack Software Developer",

  description:
    "Portfolio of Akahalu Vitalis, a full-stack software developer building secure web APIs, responsive web applications, and mobile-ready digital products.",

  url: env.appUrl,
  apiUrl: env.apiUrl,

  navigation: [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "About",
      href: "/about",
    },
    {
      label: "Projects",
      href: "/projects",
    },
    {
      label: "Experience",
      href: "/experience",
    },
    {
      label: "Contact",
      href: "/contact",
    },
  ],
} as const

export type SiteNavigationItem =
  (typeof siteConfig.navigation)[number]