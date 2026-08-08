import {
  ArrowRight,
  BriefcaseBusiness,
  FolderKanban,
  Mail,
  UserRound,
} from "lucide-react"
import Link from "next/link"

const dashboardActions = [
  {
    title: "Portfolio profile",
    description:
      "Manage your biography, public details, availability and SEO.",
    href: "/admin/profile",
    icon: UserRound,
  },
  {
    title: "Projects",
    description:
      "Create and manage portfolio projects, links, media and technologies.",
    href: "/admin/projects",
    icon: FolderKanban,
  },
  {
    title: "Experience",
    description:
      "Maintain your professional work history and featured experience.",
    href: "/admin/experience",
    icon: BriefcaseBusiness,
  },
  {
    title: "Contact inquiries",
    description:
      "Review and manage messages received through the public website.",
    href: "/admin/inquiries",
    icon: Mail,
  },
] as const

export default function AdminDashboardPage() {
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
          areas that power your public portfolio.
        </p>
      </div>

      <section className="mt-10">
        <h2 className="text-lg font-semibold">
          Quick actions
        </h2>

        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {dashboardActions.map(
            (action) => {
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
                    {action.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {action.description}
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
      </section>

      <section className="mt-8 rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="font-semibold">
          Administration status
        </h2>

        <div className="mt-4 flex items-center gap-3">
          <span
            className="size-2.5 rounded-full bg-emerald-500"
            aria-hidden="true"
          />

          <p className="text-sm text-muted-foreground">
            Secure administrator authentication
            and session management are active.
          </p>
        </div>
      </section>
    </div>
  )
}