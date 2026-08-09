import {
  BriefcaseBusiness,
  FolderKanban,
  Gauge,
  Layers3,
  Mail,
  UserRound,
  Users,
  Wrench,
  type LucideIcon,
} from "lucide-react"

export type AdminNavigationItem = {
  title: string
  href: string
  icon: LucideIcon
  permission?: string
  superuserOnly?: boolean
}

export const adminNavigation: AdminNavigationItem[] = [
  {
    title:
      "Dashboard",

    href:
      "/admin",

    icon:
      Gauge,
  },
  {
    title:
      "Profile",

    href:
      "/admin/profile",

    icon:
      UserRound,

    permission:
      "profile.read",
  },
  {
    title:
      "Projects",

    href:
      "/admin/projects",

    icon:
      FolderKanban,

    permission:
      "projects.read",
  },
  {
    title:
      "Categories",

    href:
      "/admin/categories",

    icon:
      Layers3,

    permission:
      "projects.read",
  },
  {
    title:
      "Technologies",

    href:
      "/admin/technologies",

    icon:
      Wrench,

    permission:
      "projects.read",
  },
  {
    title:
      "Experience",

    href:
      "/admin/experience",

    icon:
      BriefcaseBusiness,

    permission:
      "experience.read",
  },
  {
    title:
      "Inquiries",

    href:
      "/admin/inquiries",

    icon:
      Mail,

    permission:
      "contact_inquiries.read",
  },
  {
    title:
      "Users",

    href:
      "/admin/users",

    icon:
      Users,

    permission:
      "users.manage",
  },
]