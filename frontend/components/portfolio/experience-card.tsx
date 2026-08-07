import {
  BriefcaseBusiness,
  Building2,
  ExternalLink,
  MapPin,
} from "lucide-react"

import { Button } from "@/components/ui/button"

import type {
  ExperienceSummary,
} from "@/types/portfolio"

type ExperienceCardProps = {
  experience: ExperienceSummary
}

const employmentLabels: Record<
  string,
  string
> = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  freelance: "Freelance",
  internship: "Internship",
  apprenticeship: "Apprenticeship",
  temporary: "Temporary",
  volunteer: "Volunteer",
  self_employed: "Self-employed",
  other: "Other",
}

const locationLabels: Record<
  string,
  string
> = {
  onsite: "On-site",
  remote: "Remote",
  hybrid: "Hybrid",
}

function formatMonthYear(
  value: string
): string {
  const date = new Date(
    `${value}T00:00:00`
  )

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value
  }

  return new Intl.DateTimeFormat(
    "en-CA",
    {
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    }
  ).format(date)
}

function ExperienceCard({
  experience,
}: ExperienceCardProps) {
  const start =
    formatMonthYear(
      experience.start_date
    )

  const end =
    experience.is_current
      ? "Present"
      : experience.end_date
        ? formatMonthYear(
            experience.end_date
          )
        : null

  return (
    <article className="relative grid gap-6 rounded-2xl border border-border/70 bg-card p-6 sm:p-8 md:grid-cols-[180px_1fr]">
      <div>
        <p className="text-sm font-medium text-muted-foreground">
          {start}
          {end
            ? ` — ${end}`
            : ""}
        </p>

        {experience.is_current ? (
          <span className="mt-3 inline-flex rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            Current
          </span>
        ) : null}

        {experience.is_featured ? (
          <span className="ml-2 mt-3 inline-flex rounded-full border border-border px-3 py-1 text-xs text-muted-foreground">
            Featured
          </span>
        ) : null}
      </div>

      <div>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold tracking-tight sm:text-2xl">
              {experience.job_title}
            </h2>

            <div className="mt-2 flex items-center gap-2 text-sm font-medium text-foreground">
              <Building2
                className="size-4 text-primary"
                aria-hidden="true"
              />

              {experience.company_name}
            </div>
          </div>

          {experience.company_website ? (
            <Button
              asChild
              size="sm"
              variant="outline"
            >
              <a
                href={
                  experience.company_website
                }
                target="_blank"
                rel="noreferrer"
              >
                Company

                <ExternalLink />
              </a>
            </Button>
          ) : null}
        </div>

        <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <BriefcaseBusiness
              className="size-4"
              aria-hidden="true"
            />

            {employmentLabels[
              experience.employment_type
            ] ??
              experience.employment_type}
          </div>

          <div>
            {locationLabels[
              experience.location_type
            ] ??
              experience.location_type}
          </div>

          {experience.location ? (
            <div className="flex items-center gap-2">
              <MapPin
                className="size-4"
                aria-hidden="true"
              />

              {experience.location}
            </div>
          ) : null}
        </div>

        <p className="mt-5 leading-7 text-muted-foreground">
          {experience.summary}
        </p>
      </div>
    </article>
  )
}

export { ExperienceCard }