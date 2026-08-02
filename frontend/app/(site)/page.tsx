import Link from "next/link"
import {
  ArrowRight,
  BriefcaseBusiness,
  CalendarDays,
  Code2,
  Database,
  ExternalLink,
  Layers3,
  MapPin,
  ShieldCheck,
} from "lucide-react"

import { Container } from "@/components/shared/container"
import { EmptyState } from "@/components/shared/empty-state"
import { Button } from "@/components/ui/button"
import { getHomepageData } from "@/lib/data/homepage"

const fallbackProfile = {
  displayName: "Akahalu Vitalis",
  professionalTitle:
    "Full-Stack Software Developer",
  headline:
    "I build secure digital products that are made to grow.",
  shortBio:
    "Software developer focused on dependable APIs, responsive web experiences, and mobile-ready application architecture.",
} as const

const capabilities = [
  {
    title: "Full-stack development",
    description:
      "Responsive frontend experiences supported by reliable backend services.",
    icon: Layers3,
  },
  {
    title: "Secure APIs",
    description:
      "Structured FastAPI services with authentication, authorization, and testing.",
    icon: ShieldCheck,
  },
  {
    title: "Data architecture",
    description:
      "Carefully modelled PostgreSQL databases, repositories, and migrations.",
    icon: Database,
  },
  {
    title: "Product engineering",
    description:
      "Maintainable code designed around real user and business requirements.",
    icon: Code2,
  },
] as const

function formatExperiencePeriod(
  startDate: string,
  endDate: string | null,
  isCurrent: boolean
): string {
  const start = new Date(startDate)

  const startLabel =
    new Intl.DateTimeFormat(
      "en-CA",
      {
        year: "numeric",
        month: "short",
      }
    ).format(start)

  if (isCurrent) {
    return `${startLabel} — Present`
  }

  if (!endDate) {
    return startLabel
  }

  const end = new Date(endDate)

  const endLabel =
    new Intl.DateTimeFormat(
      "en-CA",
      {
        year: "numeric",
        month: "short",
      }
    ).format(end)

  return `${startLabel} — ${endLabel}`
}

export default async function HomePage() {
  const {
    profile,
    featuredProjects,
    featuredExperiences,
  } = await getHomepageData()

  const displayName =
    profile?.display_name ??
    fallbackProfile.displayName

  const professionalTitle =
    profile?.professional_title ??
    fallbackProfile.professionalTitle

  const headline =
    profile?.headline ??
    fallbackProfile.headline

  const shortBio =
    profile?.short_bio ??
    fallbackProfile.shortBio

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="grid min-h-[calc(100vh-4rem)] items-center gap-14 py-20 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="max-w-3xl">
            <p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              {professionalTitle}
            </p>

            <h1 className="text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-7xl">
              {headline}
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
              {shortBio}
            </p>

            {profile?.location ? (
              <div className="mt-5 flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin
                  className="size-4"
                  aria-hidden="true"
                />

                <span>
                  {profile.location}
                  {profile.country
                    ? `, ${profile.country}`
                    : ""}
                </span>
              </div>
            ) : null}

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button
                asChild
                size="lg"
              >
                <Link href="/projects">
                  Explore my work

                  <ArrowRight />
                </Link>
              </Button>

              <Button
                asChild
                size="lg"
                variant="outline"
              >
                <Link href="/contact">
                  Start a conversation
                </Link>
              </Button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-8 rounded-full bg-primary/15 blur-3xl" />

            <div className="relative rounded-3xl border border-border/70 bg-card p-6 shadow-2xl shadow-primary/5 sm:p-8">
              <div className="flex items-center gap-4">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary text-lg font-bold text-primary-foreground">
                  AV
                </div>

                <div className="min-w-0">
                  <p className="truncate font-semibold">
                    {displayName}
                  </p>

                  <p className="truncate text-sm text-muted-foreground">
                    {professionalTitle}
                  </p>
                </div>
              </div>

              <div className="mt-8 grid gap-4">
                {[
                  "FastAPI and Python",
                  "Next.js and TypeScript",
                  "PostgreSQL and Redis",
                  "Web and mobile architecture",
                ].map((skill) => (
                  <div
                    key={skill}
                    className="flex items-center gap-3 rounded-xl border border-border/60 bg-background/50 px-4 py-3"
                  >
                    <span className="size-2 shrink-0 rounded-full bg-primary" />

                    <span className="text-sm font-medium">
                      {skill}
                    </span>
                  </div>
                ))}
              </div>

              {profile?.availability_message ? (
                <p className="mt-6 rounded-xl bg-muted/50 px-4 py-3 text-sm leading-6 text-muted-foreground">
                  {profile.availability_message}
                </p>
              ) : null}
            </div>
          </div>
        </Container>
      </section>

      <section className="py-24">
        <Container>
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              What I do
            </p>

            <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              Engineering across the full product stack
            </h2>

            <p className="mt-4 text-lg leading-8 text-muted-foreground">
              I combine backend engineering, frontend development, data modelling,
              and security practices to build complete products.
            </p>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {capabilities.map((capability) => {
              const Icon = capability.icon

              return (
                <article
                  key={capability.title}
                  className="rounded-2xl border border-border/70 bg-card p-6 transition-transform duration-200 hover:-translate-y-1"
                >
                  <div className="flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <Icon
                      className="size-5"
                      aria-hidden="true"
                    />
                  </div>

                  <h3 className="mt-5 font-semibold">
                    {capability.title}
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-muted-foreground">
                    {capability.description}
                  </p>
                </article>
              )
            })}
          </div>
        </Container>
      </section>

      <section className="border-y border-border/60 bg-muted/20 py-24">
        <Container>
          <div className="flex flex-col gap-6 sm:flex-row sm:items-end sm:justify-between">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                Featured projects
              </p>

              <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
                Selected work
              </h2>

              <p className="mt-4 text-lg leading-8 text-muted-foreground">
                A selection of projects demonstrating product thinking,
                engineering discipline, and full-stack development.
              </p>
            </div>

            <Button
              asChild
              variant="outline"
            >
              <Link href="/projects">
                View all projects

                <ArrowRight />
              </Link>
            </Button>
          </div>

          <div className="mt-12">
            {featuredProjects.length ? (
              <div className="grid gap-6 lg:grid-cols-3">
                {featuredProjects.map(
                  (project) => (
                    <article
                      key={project.id}
                      className="flex h-full flex-col rounded-2xl border border-border/70 bg-card p-6"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        {project.category ? (
                          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                            {project.category.name}
                          </span>
                        ) : null}

                        {project.is_featured ? (
                          <span className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
                            Featured
                          </span>
                        ) : null}
                      </div>

                      <h3 className="mt-5 text-xl font-semibold">
                        {project.title}
                      </h3>

                      <p className="mt-3 flex-1 text-sm leading-6 text-muted-foreground">
                        {project.short_description}
                      </p>

                      {project.technologies.length ? (
                        <div className="mt-5 flex flex-wrap gap-2">
                          {project.technologies
                            .slice(0, 4)
                            .map(
                              (technology) => (
                                <span
                                  key={
                                    technology.id
                                  }
                                  className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium"
                                >
                                  {
                                    technology.name
                                  }
                                </span>
                              )
                            )}
                        </div>
                      ) : null}

                      <Button
                        asChild
                        variant="link"
                        className="mt-5 h-auto justify-start px-0"
                      >
                        <Link
                          href={`/projects/${project.slug}`}
                        >
                          View project

                          <ExternalLink />
                        </Link>
                      </Button>
                    </article>
                  )
                )}
              </div>
            ) : (
              <EmptyState
                title="Projects are coming soon"
                description="Featured projects will appear here once they are published through the portfolio administration system."
              />
            )}
          </div>
        </Container>
      </section>

      <section className="py-24">
        <Container>
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Experience
            </p>

            <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              Professional journey
            </h2>

            <p className="mt-4 text-lg leading-8 text-muted-foreground">
              Selected roles and engagements that have shaped my engineering
              experience.
            </p>
          </div>

          <div className="mt-12">
            {featuredExperiences.length ? (
              <div className="grid gap-6 lg:grid-cols-3">
                {featuredExperiences.map(
                  (experience) => (
                    <article
                      key={experience.id}
                      className="rounded-2xl border border-border/70 bg-card p-6"
                    >
                      <div className="flex size-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
                        <BriefcaseBusiness
                          className="size-5"
                          aria-hidden="true"
                        />
                      </div>

                      <h3 className="mt-5 text-lg font-semibold">
                        {experience.job_title}
                      </h3>

                      <p className="mt-1 font-medium text-muted-foreground">
                        {
                          experience.company_name
                        }
                      </p>

                      <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
                        <CalendarDays
                          className="size-4"
                          aria-hidden="true"
                        />

                        <span>
                          {formatExperiencePeriod(
                            experience.start_date,
                            experience.end_date,
                            experience.is_current
                          )}
                        </span>
                      </div>

                      {experience.location ? (
                        <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
                          <MapPin
                            className="size-4"
                            aria-hidden="true"
                          />

                          <span>
                            {
                              experience.location
                            }
                          </span>
                        </div>
                      ) : null}

                      <p className="mt-5 text-sm leading-6 text-muted-foreground">
                        {experience.summary}
                      </p>
                    </article>
                  )
                )}
              </div>
            ) : (
              <EmptyState
                title="Experience will be added soon"
                description="Professional experience will appear here once public records are published."
              />
            )}
          </div>

          <div className="mt-8">
            <Button
              asChild
              variant="outline"
            >
              <Link href="/experience">
                View experience

                <ArrowRight />
              </Link>
            </Button>
          </div>
        </Container>
      </section>
    </>
  )
}