import type { Metadata } from "next"
import Link from "next/link"

import { ExperienceCard } from "@/components/portfolio/experience-card"
import { ExperienceFilters } from "@/components/portfolio/experience-filters"
import { ExperiencePagination } from "@/components/portfolio/experience-pagination"
import { Container } from "@/components/shared/container"
import { EmptyState } from "@/components/shared/empty-state"
import { Button } from "@/components/ui/button"
import { getExperienceDirectoryData } from "@/lib/data/experiences"

import type {
  PublicExperienceListParams,
} from "@/services/portfolio/server-service"

export const metadata: Metadata = {
  title: "Experience",
  description:
    "Explore the professional experience, software development work, and technical responsibilities of Akahalu Vitalis.",

  alternates: {
    canonical: "/experience",
  },
}

type ExperiencePageProps = {
  searchParams?: Promise<{
    page?: string
    search?: string
    employment?: string
    location?: string
    current?: string
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

function parseBoolean(
  value: string | undefined
): boolean | undefined {
  if (value === "true") {
    return true
  }

  if (value === "false") {
    return false
  }

  return undefined
}

export default async function ExperiencePage({
  searchParams,
}: ExperiencePageProps) {
  const params =
    await searchParams

  const page =
    parsePage(params?.page)

  const search =
    params?.search?.trim() ?? ""

  const employmentType =
    params?.employment?.trim() ?? ""

  const locationType =
    params?.location?.trim() ?? ""

  const current =
    params?.current?.trim() ?? ""

  const apiParams: PublicExperienceListParams = {
    page,
    page_size: 12,
    search:
      search || undefined,
    employment_type:
      employmentType || undefined,
    location_type:
      locationType || undefined,
    is_current:
      parseBoolean(current),
  }

  const experiences =
    await getExperienceDirectoryData(
      apiParams
    )

  const hasFilters =
    Boolean(search) ||
    Boolean(employmentType) ||
    Boolean(locationType) ||
    Boolean(current)

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="py-20 sm:py-24 lg:py-28">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Experience
            </p>

            <h1 className="mt-4 text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Professional experience
            </h1>

            <p className="mt-6 text-lg leading-8 text-muted-foreground sm:text-xl">
              A timeline of professional work,
              software engineering responsibilities,
              technical contributions, and practical
              experience.
            </p>
          </div>
        </Container>
      </section>

      <section className="py-16 sm:py-20">
        <Container>
          <ExperienceFilters
            search={search}
            employmentType={
              employmentType
            }
            locationType={
              locationType
            }
            current={current}
          />

          <div className="mt-8 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-muted-foreground">
              {experiences.total_items === 1
                ? "1 public experience"
                : `${experiences.total_items} public experiences`}
            </p>

            {hasFilters ? (
              <p className="text-sm text-muted-foreground">
                Showing filtered results
              </p>
            ) : null}
          </div>

          <div className="mt-8">
            {experiences.items.length ? (
              <>
                <div className="relative space-y-6">
                  <div
                    aria-hidden="true"
                    className="absolute bottom-0 left-5 top-0 hidden w-px bg-border lg:block"
                  />

                  {experiences.items.map(
                    (experience) => (
                      <div
                        key={experience.id}
                        className="relative lg:pl-12"
                      >
                        <div
                          aria-hidden="true"
                          className="absolute left-[15px] top-9 hidden size-[11px] rounded-full border-2 border-background bg-primary lg:block"
                        />

                        <ExperienceCard
                          experience={
                            experience
                          }
                        />
                      </div>
                    )
                  )}
                </div>

                <ExperiencePagination
                  page={
                    experiences.page
                  }
                  totalPages={
                    experiences.total_pages
                  }
                  search={
                    search || undefined
                  }
                  employmentType={
                    employmentType ||
                    undefined
                  }
                  locationType={
                    locationType ||
                    undefined
                  }
                  current={
                    current || undefined
                  }
                />
              </>
            ) : (
              <EmptyState
                title={
                  hasFilters
                    ? "No matching experience"
                    : "Experience is being prepared"
                }
                description={
                  hasFilters
                    ? "Try changing or clearing the current filters."
                    : "Public professional experience will appear here once it has been added to the portfolio."
                }
                action={
                  hasFilters ? (
                    <Button asChild>
                      <Link href="/experience">
                        Clear filters
                      </Link>
                    </Button>
                  ) : (
                    <Button asChild>
                      <Link href="/contact">
                        Contact me
                      </Link>
                    </Button>
                  )
                }
              />
            )}
          </div>
        </Container>
      </section>

      <section className="border-t border-border/60 bg-muted/20 py-16 sm:py-20">
        <Container className="grid gap-6 sm:grid-cols-[1fr_auto] sm:items-center">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">
              Interested in working together?
            </h2>

            <p className="mt-2 max-w-2xl text-muted-foreground">
              I am open to discussing software
              development opportunities,
              collaborations, and technically
              challenging projects.
            </p>
          </div>

          <Button
            asChild
            size="lg"
          >
            <Link href="/contact">
              Start a conversation
            </Link>
          </Button>
        </Container>
      </section>
    </>
  )
}