import Link from "next/link"
import {
  ArrowRight,
  Code2,
  Database,
  Layers3,
  ShieldCheck,
} from "lucide-react"

import { Container } from "@/components/shared/container"
import { Button } from "@/components/ui/button"

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

export default function HomePage() {
  return (
    <>
      <section className="border-b border-border/60">
        <Container className="grid min-h-[calc(100vh-4rem)] items-center gap-14 py-20 lg:grid-cols-[1.2fr_0.8fr]">
          <div className="max-w-3xl">
            <p className="mb-5 text-sm font-semibold uppercase tracking-[0.2em] text-primary">
              Full-stack software developer
            </p>

            <h1 className="text-4xl font-bold tracking-tight text-balance sm:text-5xl lg:text-7xl">
              I build secure digital products that are made to grow.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground sm:text-xl">
              I&apos;m Akahalu Vitalis, a software developer focused on
              dependable APIs, responsive web experiences, and
              mobile-ready application architecture.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/projects">
                  Explore my work
                  <ArrowRight />
                </Link>
              </Button>

              <Button asChild size="lg" variant="outline">
                <Link href="/contact">Start a conversation</Link>
              </Button>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-8 rounded-full bg-primary/15 blur-3xl" />

            <div className="relative rounded-3xl border border-border/70 bg-card p-6 shadow-2xl shadow-primary/5 sm:p-8">
              <div className="flex items-center gap-4">
                <div className="flex size-14 items-center justify-center rounded-2xl bg-primary text-lg font-bold text-primary-foreground">
                  AV
                </div>

                <div>
                  <p className="font-semibold">Akahalu Vitalis</p>

                  <p className="text-sm text-muted-foreground">
                    Software developer
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
                    <span className="size-2 rounded-full bg-primary" />

                    <span className="text-sm font-medium">{skill}</span>
                  </div>
                ))}
              </div>
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
              I combine backend engineering, frontend development, data
              modelling, and security practices to build complete products.
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
                    <Icon className="size-5" aria-hidden="true" />
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
    </>
  )
}