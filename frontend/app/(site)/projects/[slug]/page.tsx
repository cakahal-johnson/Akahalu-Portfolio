import type { Metadata } from "next"
import {
  ArrowLeft,
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  CheckCircle2,
  Code2,
  ExternalLink,
  Layers3,
} from "lucide-react"
import { FaGithub } from "react-icons/fa"
import Link from "next/link"
import { notFound } from "next/navigation"

import { Container } from "@/components/shared/container"
import { Button } from "@/components/ui/button"
import { siteConfig } from "@/config/site"
import { getPublicProject } from "@/lib/data/projects"

import type {
  ProjectLinkRead,
  ProjectRead,
} from "@/types/portfolio"

type ProjectPageProps = {
  params: Promise<{
    slug: string
  }>
}

function formatProjectDate(
  value: string | null
): string | null {
  if (!value) {
    return null
  }

  const date =
    new Date(value)

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return null
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      year: "numeric",
      month: "short",
    }
  ).format(date)
}

function getProjectPeriod(
  project: ProjectRead
): string | null {
  const start =
    formatProjectDate(
      project.started_at
    )

  const end =
    formatProjectDate(
      project.completed_at
    )

  if (start && end) {
    return `${start} — ${end}`
  }

  if (start) {
    return start
  }

  if (end) {
    return end
  }

  return null
}

function getLinkIcon(
  link: ProjectLinkRead
) {
  if (
    link.link_type ===
    "repository"
  ) {
    return FaGithub
  }

  return ExternalLink
}

export async function generateMetadata({
  params,
}: ProjectPageProps): Promise<Metadata> {
  const { slug } =
    await params

  const project =
    await getPublicProject(slug)

  if (!project) {
    return {
      title: "Project not found",
    }
  }

  const title =
    project.seo_title ??
    project.title

  const description =
    project.seo_description ??
    project.short_description

  return {
    title:
      project.seo_title
        ? {
            absolute:
              project.seo_title,
          }
        : project.title,

    description,

    alternates: {
      canonical:
        `/projects/${project.slug}`,
    },

    openGraph: {
      title,
      description,
      url:
        `/projects/${project.slug}`,
      siteName:
        siteConfig.name,
      type: "article",
    },

    twitter: {
      card:
        "summary_large_image",
      title,
      description,
    },
  }
}

export default async function ProjectPage({
  params,
}: ProjectPageProps) {
  const { slug } =
    await params

  const project =
    await getPublicProject(slug)

  if (!project) {
    notFound()
  }

  const projectPeriod =
    getProjectPeriod(project)

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="py-16 sm:py-20 lg:py-24">
          <Button
            asChild
            variant="ghost"
            className="-ml-3 mb-8"
          >
            <Link href="/projects">
              <ArrowLeft />

              All projects
            </Link>
          </Button>

          <div className="max-w-4xl">
            <div className="flex flex-wrap gap-2">
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

            <h1 className="mt-5 text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              {project.title}
            </h1>

            <p className="mt-6 max-w-3xl text-lg leading-8 text-muted-foreground sm:text-xl">
              {
                project.short_description
              }
            </p>

            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-muted-foreground">
              {projectPeriod ? (
                <div className="flex items-center gap-2">
                  <CalendarDays
                    className="size-4"
                    aria-hidden="true"
                  />

                  {projectPeriod}
                </div>
              ) : null}

              {project.technologies.length ? (
                <div className="flex items-center gap-2">
                  <Layers3
                    className="size-4"
                    aria-hidden="true"
                  />

                  {
                    project.technologies
                      .length
                  }{" "}
                  technologies
                </div>
              ) : null}
            </div>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              {project.live_url ? (
                <Button
                  asChild
                  size="lg"
                >
                  <a
                    href={
                      project.live_url
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    Live project

                    <ArrowUpRight />
                  </a>
                </Button>
              ) : null}

              {project.repository_url ? (
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                >
                  <a
                    href={
                      project.repository_url
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    <FaGithub  />

                    Source code
                  </a>
                </Button>
              ) : null}
            </div>
          </div>
        </Container>
      </section>

      {project.thumbnail_url ? (
        <section className="border-b border-border/60 bg-muted/20 py-10 sm:py-14">
          <Container>
            <div className="overflow-hidden rounded-3xl border border-border/70 bg-muted">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={
                  project.thumbnail_url
                }
                alt={`${project.title} preview`}
                className="w-full object-cover"
              />
            </div>
          </Container>
        </section>
      ) : null}

      <section className="py-20 sm:py-24">
        <Container>
          <div className="grid gap-12 lg:grid-cols-[1fr_320px] lg:gap-20">
            <div className="space-y-14">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                  Overview
                </p>

                <h2 className="mt-4 text-3xl font-bold tracking-tight">
                  About this project
                </h2>

                <p className="mt-6 whitespace-pre-line leading-8 text-muted-foreground">
                  {
                    project.description
                  }
                </p>
              </div>

              {project.problem_statement ? (
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                    Challenge
                  </p>

                  <h2 className="mt-4 text-2xl font-bold tracking-tight">
                    The problem
                  </h2>

                  <p className="mt-5 whitespace-pre-line leading-8 text-muted-foreground">
                    {
                      project.problem_statement
                    }
                  </p>
                </div>
              ) : null}

              {project.solution_summary ? (
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                    Solution
                  </p>

                  <h2 className="mt-4 text-2xl font-bold tracking-tight">
                    The approach
                  </h2>

                  <p className="mt-5 whitespace-pre-line leading-8 text-muted-foreground">
                    {
                      project.solution_summary
                    }
                  </p>
                </div>
              ) : null}

              {project.key_features ? (
                <div>
                  <div className="flex items-center gap-3">
                    <CheckCircle2
                      className="size-5 text-primary"
                      aria-hidden="true"
                    />

                    <h2 className="text-2xl font-bold tracking-tight">
                      Key features
                    </h2>
                  </div>

                  <p className="mt-5 whitespace-pre-line leading-8 text-muted-foreground">
                    {
                      project.key_features
                    }
                  </p>
                </div>
              ) : null}

              {project.technical_highlights ? (
                <div>
                  <div className="flex items-center gap-3">
                    <Code2
                      className="size-5 text-primary"
                      aria-hidden="true"
                    />

                    <h2 className="text-2xl font-bold tracking-tight">
                      Technical highlights
                    </h2>
                  </div>

                  <p className="mt-5 whitespace-pre-line leading-8 text-muted-foreground">
                    {
                      project.technical_highlights
                    }
                  </p>
                </div>
              ) : null}
            </div>

            <aside className="space-y-6 lg:sticky lg:top-24 lg:self-start">
              {project.technologies.length ? (
                <div className="rounded-2xl border border-border/70 bg-card p-6">
                  <h2 className="font-semibold">
                    Technologies
                  </h2>

                  <div className="mt-4 flex flex-wrap gap-2">
                    {project.technologies.map(
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
                </div>
              ) : null}

              {project.links.length ? (
                <div className="rounded-2xl border border-border/70 bg-card p-6">
                  <h2 className="font-semibold">
                    Project links
                  </h2>

                  <div className="mt-4 grid gap-2">
                    {project.links.map(
                      (link) => {
                        const Icon =
                          getLinkIcon(
                            link
                          )

                        return (
                          <Button
                            key={
                              link.id
                            }
                            asChild
                            variant="outline"
                            className="justify-start"
                          >
                            <a
                              href={
                                link.url
                              }
                              target={
                                link.opens_in_new_tab
                                  ? "_blank"
                                  : undefined
                              }
                              rel={
                                link.opens_in_new_tab
                                  ? "noreferrer"
                                  : undefined
                              }
                            >
                              <Icon />

                              {
                                link.label
                              }
                            </a>
                          </Button>
                        )
                      }
                    )}
                  </div>
                </div>
              ) : null}
            </aside>
          </div>
        </Container>
      </section>

      <section className="border-t border-border/60 bg-muted/20 py-16">
        <Container className="flex flex-col gap-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-semibold">
              Explore more work
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Browse the complete portfolio project collection.
            </p>
          </div>

          <Button
            asChild
            variant="outline"
          >
            <Link href="/projects">
              All projects

              <ArrowRight />
            </Link>
          </Button>
        </Container>
      </section>
    </>
  )
}