import type { Metadata } from "next"
import Link from "next/link"

import { ProjectCard } from "@/components/portfolio/project-card"
import { ProjectFilters } from "@/components/portfolio/project-filters"
import { ProjectPagination } from "@/components/portfolio/project-pagination"
import { Container } from "@/components/shared/container"
import { EmptyState } from "@/components/shared/empty-state"
import { Button } from "@/components/ui/button"
import { getProjectDirectoryData } from "@/lib/data/projects"

import type {
  PublicProjectListParams,
} from "@/types/portfolio"

export const metadata: Metadata = {
  title: "Projects",
  description:
    "Explore software projects by Akahalu Vitalis, including full-stack applications, backend APIs, databases, and modern digital products.",

  alternates: {
    canonical: "/projects",
  },
}

type ProjectsPageProps = {
  searchParams?: Promise<{
    page?: string
    search?: string
    category?: string
    technology?: string
  }>
}

function parsePage(
  value: string | undefined
): number {
  const parsed =
    Number.parseInt(
      value ?? "1",
      10
    )

  return Number.isFinite(parsed) &&
    parsed > 0
    ? parsed
    : 1
}

export default async function ProjectsPage({
  searchParams,
}: ProjectsPageProps) {
  const params =
    await searchParams

  const page =
    parsePage(params?.page)

  const search =
    params?.search?.trim() ?? ""

  const categorySlug =
    params?.category?.trim() ?? ""

  const technologySlug =
    params?.technology?.trim() ?? ""

  const apiParams: PublicProjectListParams = {
    page,
    page_size: 9,

    search:
      search || undefined,

    category_slug:
      categorySlug || undefined,

    technology_slug:
      technologySlug || undefined,
  }

  const {
    projects,
    categories,
    technologies,
  } = await getProjectDirectoryData(
    apiParams
  )

  const hasFilters =
    Boolean(search) ||
    Boolean(categorySlug) ||
    Boolean(technologySlug)

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="py-20 sm:py-24 lg:py-28">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Projects
            </p>

            <h1 className="mt-4 text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Software built with purpose
            </h1>

            <p className="mt-6 text-lg leading-8 text-muted-foreground sm:text-xl">
              Explore projects spanning backend APIs,
              full-stack applications, databases,
              security, and modern product engineering.
            </p>
          </div>
        </Container>
      </section>

      <section className="py-16 sm:py-20">
        <Container>
          <ProjectFilters
            search={search}
            categorySlug={
              categorySlug
            }
            technologySlug={
              technologySlug
            }
            categories={categories}
            technologies={
              technologies
            }
          />

          <div className="mt-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              {projects.total_items === 1
                ? "1 published project"
                : `${projects.total_items} published projects`}
            </p>

            {hasFilters ? (
              <p className="text-sm text-muted-foreground">
                Showing filtered results
              </p>
            ) : null}
          </div>

          <div className="mt-8">
            {projects.items.length ? (
              <>
                <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
                  {projects.items.map(
                    (project) => (
                      <ProjectCard
                        key={project.id}
                        project={project}
                      />
                    )
                  )}
                </div>

                <ProjectPagination
                  page={projects.page}
                  totalPages={
                    projects.total_pages
                  }
                  search={
                    search ||
                    undefined
                  }
                  categorySlug={
                    categorySlug ||
                    undefined
                  }
                  technologySlug={
                    technologySlug ||
                    undefined
                  }
                />
              </>
            ) : (
              <EmptyState
                title={
                  hasFilters
                    ? "No matching projects"
                    : "Projects are coming soon"
                }
                description={
                  hasFilters
                    ? "Try changing or clearing the current search filters."
                    : "Published portfolio projects will appear here as they are added."
                }
                action={
                  hasFilters ? (
                    <Button asChild>
                      <Link href="/projects">
                        Clear filters
                      </Link>
                    </Button>
                  ) : undefined
                }
              />
            )}
          </div>
        </Container>
      </section>
    </>
  )
}