export const siteConfig = {
  name: "Akahalu Vitalis",
  shortName: "Akahalu",
  title: "Akahalu Vitalis | Full-Stack Software Developer",
  description:
    "Portfolio of Akahalu Vitalis, a full-stack software developer building secure web APIs, responsive web applications, and mobile-ready digital products.",
  url: "http://localhost:3000",
  apiUrl: "http://127.0.0.1:8000/api/v1",
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