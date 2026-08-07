import type { Metadata } from "next"
import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  Download,
  Globe2,
  Mail,
  MapPin,
} from "lucide-react"
import Link from "next/link"

import { Container } from "@/components/shared/container"
import { EmptyState } from "@/components/shared/empty-state"
import { Button } from "@/components/ui/button"
import { siteConfig } from "@/config/site"
import { getPublicProfile } from "@/lib/data/profile"

import type {
  ProfileAvailabilityStatus,
  ProfileRead,
} from "@/types/portfolio"

const availabilityLabels: Record<
  ProfileAvailabilityStatus,
  string
> = {
  available: "Available",
  open_to_opportunities: "Open to opportunities",
  limited_availability: "Limited availability",
  unavailable: "Currently unavailable",
}

const principles = [
  {
    title: "Security by design",
    description:
      "Authentication, authorization, validation, and defensive application design are treated as core architecture rather than afterthoughts.",
  },
  {
    title: "Maintainable engineering",
    description:
      "I favour clear boundaries, typed contracts, testing, and predictable project structure so applications remain easier to evolve.",
  },
  {
    title: "Full-stack thinking",
    description:
      "I consider the complete path from database design and APIs to responsive interfaces and the user experience they support.",
  },
  {
    title: "Production mindset",
    description:
      "I build with deployment, observability, data integrity, performance, and long-term maintainability in mind.",
  },
] as const

function getInitials(
  displayName: string
): string {
  const parts = displayName
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (!parts.length) {
    return "AV"
  }

  return parts
    .slice(0, 2)
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
}

function ProfilePortrait({
  profile,
}: {
  profile: ProfileRead
}) {
  const initials = getInitials(
    profile.display_name
  )

  if (profile.profile_image_url) {
    return (
      <div className="relative aspect-[4/5] overflow-hidden rounded-3xl border border-border/70 bg-muted">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={profile.profile_image_url}
          alt={`Portrait of ${profile.display_name}`}
          className="size-full object-cover"
        />
      </div>
    )
  }

  return (
    <div className="relative flex aspect-[4/5] items-center justify-center overflow-hidden rounded-3xl border border-border/70 bg-card">
      <div className="absolute inset-0 bg-gradient-to-br from-primary/15 via-transparent to-primary/5" />

      <div className="absolute left-1/2 top-1/2 size-72 -translate-x-1/2 -translate-y-1/2 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative flex size-32 items-center justify-center rounded-3xl bg-primary text-4xl font-bold tracking-tight text-primary-foreground shadow-xl sm:size-40 sm:text-5xl">
        {initials}
      </div>
    </div>
  )
}

export async function generateMetadata(): Promise<Metadata> {
  const profile = await getPublicProfile()

  if (!profile) {
    return {
      title: "About",
      description:
        "Learn more about Akahalu Vitalis and his approach to full-stack software development.",
      alternates: {
        canonical: "/about",
      },
    }
  }

  const description =
    profile.seo_description ??
    profile.short_bio ??
    siteConfig.description

  const title =
    profile.seo_title ??
    `About ${profile.display_name}`

  return {
    title: profile.seo_title
      ? {
          absolute: profile.seo_title,
        }
      : "About",

    description,

    alternates: {
      canonical: "/about",
    },

    openGraph: {
      title,
      description,
      url: "/about",
      siteName: siteConfig.name,
    },

    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
  }
}

export default async function AboutPage() {
  const profile = await getPublicProfile()

  if (!profile) {
    return (
      <Container className="py-24 sm:py-32">
        <EmptyState
          title="Profile information is unavailable"
          description="The public portfolio profile is currently unavailable. Please check back again soon."
          action={
            <Button asChild>
              <Link href="/">
                Return home
              </Link>
            </Button>
          }
        />
      </Container>
    )
  }

  const availabilityLabel =
    availabilityLabels[
      profile.availability_status
    ]

  const location = [
    profile.location,
    profile.country,
  ]
    .filter(Boolean)
    .join(", ")

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="grid gap-14 py-20 sm:py-24 lg:grid-cols-[0.8fr_1.2fr] lg:items-center lg:gap-20 lg:py-32">
          <div className="mx-auto w-full max-w-md lg:mx-0">
            <ProfilePortrait
              profile={profile}
            />
          </div>

          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              About me
            </p>

            <h1 className="mt-4 text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              {profile.display_name}
            </h1>

            <p className="mt-4 text-xl font-medium text-foreground sm:text-2xl">
              {profile.professional_title}
            </p>

            <p className="mt-6 text-lg leading-8 text-muted-foreground">
              {profile.headline}
            </p>

            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm text-muted-foreground">
              {location ? (
                <div className="flex items-center gap-2">
                  <MapPin
                    className="size-4 shrink-0"
                    aria-hidden="true"
                  />

                  <span>{location}</span>
                </div>
              ) : null}

              <div className="flex items-center gap-2">
                <CheckCircle2
                  className="size-4 shrink-0 text-primary"
                  aria-hidden="true"
                />

                <span>
                  {availabilityLabel}
                </span>
              </div>

              {profile.years_of_experience > 0 ? (
                <div className="flex items-center gap-2">
                  <BriefcaseBusiness
                    className="size-4 shrink-0"
                    aria-hidden="true"
                  />

                  <span>
                    {profile.years_of_experience}+
                    {profile.years_of_experience === 1
                      ? " year"
                      : " years"}{" "}
                    of experience
                  </span>
                </div>
              ) : null}
            </div>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Button
                asChild
                size="lg"
              >
                <Link href="/contact">
                  Start a conversation

                  <ArrowRight />
                </Link>
              </Button>

              <Button
                asChild
                size="lg"
                variant="outline"
              >
                <a
                  href={`mailto:${profile.primary_email}`}
                >
                  <Mail />

                  Email me
                </a>
              </Button>

              {profile.resume_url ? (
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                >
                  <a
                    href={profile.resume_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Download />

                    Resume
                  </a>
                </Button>
              ) : null}
            </div>
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-24">
        <Container>
          <div className="grid gap-12 lg:grid-cols-[0.75fr_1.25fr] lg:gap-20">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                My story
              </p>

              <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
                Building technology with purpose
              </h2>
            </div>

            <div className="space-y-6 text-base leading-8 text-muted-foreground sm:text-lg">
              <p>
                {profile.biography}
              </p>

              <p>
                {profile.short_bio}
              </p>
            </div>
          </div>
        </Container>
      </section>

      <section className="border-y border-border/60 bg-muted/20 py-20 sm:py-24">
        <Container>
          <div className="max-w-2xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              How I work
            </p>

            <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
              Engineering principles that guide my work
            </h2>

            <p className="mt-4 text-lg leading-8 text-muted-foreground">
              My approach combines software engineering fundamentals with practical product thinking.
            </p>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-2">
            {principles.map(
              (principle) => (
                <article
                  key={principle.title}
                  className="rounded-2xl border border-border/70 bg-card p-6 sm:p-8"
                >
                  <h3 className="text-lg font-semibold">
                    {principle.title}
                  </h3>

                  <p className="mt-3 leading-7 text-muted-foreground">
                    {
                      principle.description
                    }
                  </p>
                </article>
              )
            )}
          </div>
        </Container>
      </section>

      <section className="py-20 sm:py-24">
        <Container>
          <div className="grid gap-8 rounded-3xl border border-border/70 bg-card p-6 sm:p-10 lg:grid-cols-[1fr_auto] lg:items-center lg:p-12">
            <div className="max-w-2xl">
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                Availability
              </p>

              <h2 className="mt-4 text-3xl font-bold tracking-tight">
                {availabilityLabel}
              </h2>

              <p className="mt-4 leading-7 text-muted-foreground">
                {profile.availability_message ??
                  "I'm open to discussing software development opportunities, collaborations, and interesting technical challenges."}
              </p>

              <div className="mt-6 flex flex-col gap-3 text-sm text-muted-foreground sm:flex-row sm:flex-wrap">
                <a
                  href={`mailto:${profile.primary_email}`}
                  className="inline-flex items-center gap-2 transition-colors hover:text-foreground"
                >
                  <Mail
                    className="size-4"
                    aria-hidden="true"
                  />

                  {profile.primary_email}
                </a>

                {profile.website_url ? (
                  <a
                    href={profile.website_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 transition-colors hover:text-foreground"
                  >
                    <Globe2
                      className="size-4"
                      aria-hidden="true"
                    />

                    Website
                  </a>
                ) : null}
              </div>
            </div>

            <Button
              asChild
              size="lg"
            >
              <Link href="/contact">
                Contact me

                <ArrowRight />
              </Link>
            </Button>
          </div>
        </Container>
      </section>
    </>
  )
}