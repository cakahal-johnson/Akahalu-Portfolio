"use client"

import {
  ArrowRight,
  BriefcaseBusiness,
  FolderKanban,
  Layers3,
  Mail,
  ShieldCheck,
  UserRound,
  Users,
  Wrench,
  type LucideIcon,
} from "lucide-react"

import Link from "next/link"

import {
  useAdminSession,
} from "@/components/admin/auth/admin-session-context"

import {
  userHasPermission,
} from "@/lib/auth/permissions"

type DashboardAction = {
  title: string

  description: string

  href: string

  icon: LucideIcon

  permission:
    string
}

const dashboardActions:
  DashboardAction[] = [
    {
      title:
        "Portfolio profile",

      description:
        "Manage your biography, public details, availability and SEO.",

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

      description:
        "Create and manage portfolio projects, publishing, links and media.",

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

      description:
        "Organize projects using managed portfolio categories.",

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

      description:
        "Maintain the technologies and tools used across portfolio projects.",

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

      description:
        "Maintain professional work history, visibility and featured experience.",

      href:
        "/admin/experience",

      icon:
        BriefcaseBusiness,

      permission:
        "experience.read",
    },
    {
      title:
        "Contact inquiries",

      description:
        "Review and manage messages received through the public website.",

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

      description:
        "Review administrator accounts, roles, permissions and account lifecycle.",

      href:
        "/admin/users",

      icon:
        Users,

      permission:
        "users.manage",
    },
  ]

export function AdminDashboard() {
  const {
    user,
  } =
    useAdminSession()

  const visibleActions =
    dashboardActions.filter(
      (
        action
      ) =>
        userHasPermission(
          user,
          action.permission
        )
    )

  return (
    <div className="mx-auto w-full max-w-7xl">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Dashboard
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Portfolio administration
        </h1>

        <p className="mt-4 max-w-3xl leading-7 text-muted-foreground">
          Manage the content and operational
          areas that power your public
          portfolio.
        </p>
      </div>

      <section className="mt-10">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              Quick actions
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Only administration areas
              available to your account are
              shown.
            </p>
          </div>

          <p className="text-sm text-muted-foreground">
            {
              visibleActions.length
            }{" "}
            available
          </p>
        </div>

        {visibleActions.length >
        0 ? (
          <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {visibleActions.map(
              (
                action
              ) => {
                const Icon =
                  action.icon

                return (
                  <Link
                    key={
                      action.href
                    }
                    href={
                      action.href
                    }
                    className="group rounded-2xl border border-border bg-background p-5 transition-all hover:-translate-y-0.5 hover:border-primary/30 hover:shadow-sm"
                  >
                    <div className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <Icon
                        className="size-5"
                        aria-hidden="true"
                      />
                    </div>

                    <h3 className="mt-5 font-semibold">
                      {
                        action.title
                      }
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-muted-foreground">
                      {
                        action.description
                      }
                    </p>

                    <div className="mt-5 flex items-center gap-2 text-sm font-medium text-primary">
                      Manage

                      <ArrowRight
                        className="size-4 transition-transform group-hover:translate-x-1"
                        aria-hidden="true"
                      />
                    </div>
                  </Link>
                )
              }
            )}
          </div>
        ) : (
          <div className="mt-4 rounded-2xl border border-dashed border-border bg-background p-8 text-center">
            <ShieldCheck
              className="mx-auto size-8 text-muted-foreground"
              aria-hidden="true"
            />

            <h3 className="mt-4 font-semibold">
              No administration areas available
            </h3>

            <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted-foreground">
              Your administrator account is
              authenticated, but it currently
              has no permissions for the
              available management areas.
            </p>
          </div>
        )}
      </section>

      <section className="mt-8 rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="font-semibold">
          Administration status
        </h2>

        <div className="mt-4 flex items-start gap-3">
          <span
            className="mt-1.5 size-2.5 shrink-0 rounded-full bg-emerald-500"
            aria-hidden="true"
          />

          <div>
            <p className="text-sm font-medium">
              Secure administration is active
            </p>

            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              Administrator authentication,
              session management, permission
              filtering and protected backend
              authorization are enabled.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}