import type { Metadata } from "next"
import {
  Clock3,
  Mail,
  MapPin,
  MessageSquareText,
  Phone,
} from "lucide-react"

import { ContactForm } from "@/components/contact/contact-form"
import { Container } from "@/components/shared/container"
import { getPublicProfile } from "@/lib/data/profile"

export const metadata: Metadata = {
  title: "Contact",

  description:
    "Contact Akahalu Vitalis about software development opportunities, projects, contracts, freelance work, and technical collaborations.",

  alternates: {
    canonical: "/contact",
  },
}

function buildLocation(
  location: string | null,
  country: string | null
): string | null {
  const values = [
    location,
    country,
  ].filter(
    (value): value is string =>
      Boolean(value)
  )

  return values.length
    ? values.join(", ")
    : null
}

export default async function ContactPage() {
  const profile =
    await getPublicProfile()

  const location =
    profile
      ? buildLocation(
          profile.location,
          profile.country
        )
      : null

  return (
    <>
      <section className="border-b border-border/60">
        <Container className="py-20 sm:py-24 lg:py-28">
          <div className="max-w-3xl">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Contact
            </p>

            <h1 className="mt-4 text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl">
              Let&apos;s build something useful
            </h1>

            <p className="mt-6 text-lg leading-8 text-muted-foreground sm:text-xl">
              Have a software opportunity, project,
              technical challenge, or collaboration in
              mind? Send the details and I&apos;ll have
              the context needed to understand what
              you&apos;re looking for.
            </p>
          </div>
        </Container>
      </section>

      <section className="py-16 sm:py-20 lg:py-24">
        <Container>
          <div className="grid gap-10 lg:grid-cols-[0.72fr_1.28fr] lg:gap-14 xl:gap-20">
            <aside className="lg:sticky lg:top-24 lg:self-start">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
                  Get in touch
                </p>

                <h2 className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">
                  Start the conversation
                </h2>

                <p className="mt-4 leading-7 text-muted-foreground">
                  Share enough detail for me to understand
                  the goal, scope, or opportunity. You can
                  also reach me directly using the contact
                  information below.
                </p>
              </div>

              <div className="mt-8 space-y-4">
                {profile?.primary_email ? (
                  <a
                    href={`mailto:${profile.primary_email}`}
                    className="group flex gap-4 rounded-2xl border border-border/70 bg-card p-4 transition-colors hover:border-primary/30"
                  >
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <Mail
                        className="size-5"
                        aria-hidden="true"
                      />
                    </div>

                    <div className="min-w-0">
                      <p className="text-sm font-medium">
                        Email
                      </p>

                      <p className="mt-1 break-all text-sm text-muted-foreground transition-colors group-hover:text-foreground">
                        {profile.primary_email}
                      </p>
                    </div>
                  </a>
                ) : null}

                {profile?.phone ? (
                  <a
                    href={`tel:${profile.phone}`}
                    className="group flex gap-4 rounded-2xl border border-border/70 bg-card p-4 transition-colors hover:border-primary/30"
                  >
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <Phone
                        className="size-5"
                        aria-hidden="true"
                      />
                    </div>

                    <div>
                      <p className="text-sm font-medium">
                        Phone
                      </p>

                      <p className="mt-1 text-sm text-muted-foreground transition-colors group-hover:text-foreground">
                        {profile.phone}
                      </p>
                    </div>
                  </a>
                ) : null}

                {location ? (
                  <div className="flex gap-4 rounded-2xl border border-border/70 bg-card p-4">
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <MapPin
                        className="size-5"
                        aria-hidden="true"
                      />
                    </div>

                    <div>
                      <p className="text-sm font-medium">
                        Location
                      </p>

                      <p className="mt-1 text-sm text-muted-foreground">
                        {location}
                      </p>
                    </div>
                  </div>
                ) : null}

                {profile?.availability_status ? (
                  <div className="flex gap-4 rounded-2xl border border-border/70 bg-card p-4">
                    <div className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary">
                      <Clock3
                        className="size-5"
                        aria-hidden="true"
                      />
                    </div>

                    <div>
                      <p className="text-sm font-medium">
                        Availability
                      </p>

                      <p className="mt-1 text-sm leading-6 text-muted-foreground">
                        {profile.availability_message ??
                          "Open to discussing suitable software development opportunities."}
                      </p>
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="mt-8 rounded-2xl bg-muted/40 p-5">
                <div className="flex items-center gap-3">
                  <MessageSquareText
                    className="size-5 text-primary"
                    aria-hidden="true"
                  />

                  <p className="font-medium">
                    Helpful details
                  </p>
                </div>

                <p className="mt-3 text-sm leading-6 text-muted-foreground">
                  For project inquiries, including the
                  objective, preferred timeline, current
                  technology stack, and expected outcome
                  makes it easier to understand the scope.
                </p>
              </div>
            </aside>

            <ContactForm />
          </div>
        </Container>
      </section>
    </>
  )
}