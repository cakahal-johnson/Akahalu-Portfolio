import {
  ArrowUpRight,
  Code2,
} from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"

import type {
  ProjectSummary,
} from "@/types/portfolio"

type ProjectCardProps = {
  project: ProjectSummary
}

function ProjectCard({
  project,
}: ProjectCardProps) {
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-border/70 bg-card">
      {project.thumbnail_url ? (
        <div className="aspect-[16/10] overflow-hidden border-b border-border/60 bg-muted">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={project.thumbnail_url}
            alt={`${project.title} project preview`}
            className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.02]"
          />
        </div>
      ) : (
        <div className="flex aspect-[16/10] items-center justify-center border-b border-border/60 bg-muted/40">
          <div className="flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Code2
              className="size-6"
              aria-hidden="true"
            />
          </div>
        </div>
      )}

      <div className="flex flex-1 flex-col p-6">
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

        <h2 className="mt-5 text-xl font-semibold tracking-tight">
          <Link
            href={`/projects/${project.slug}`}
            className="transition-colors hover:text-primary"
          >
            {project.title}
          </Link>
        </h2>

        <p className="mt-3 flex-1 text-sm leading-6 text-muted-foreground">
          {project.short_description}
        </p>

        {project.technologies.length ? (
          <div className="mt-5 flex flex-wrap gap-2">
            {project.technologies
              .slice(0, 5)
              .map((technology) => (
                <span
                  key={technology.id}
                  className="rounded-md bg-muted px-2.5 py-1 text-xs font-medium"
                >
                  {technology.name}
                </span>
              ))}
          </div>
        ) : null}

        <Button
          asChild
          variant="link"
          className="mt-6 h-auto justify-start px-0"
        >
          <Link
            href={`/projects/${project.slug}`}
          >
            View project

            <ArrowUpRight />
          </Link>
        </Button>
      </div>
    </article>
  )
}

export { ProjectCard }