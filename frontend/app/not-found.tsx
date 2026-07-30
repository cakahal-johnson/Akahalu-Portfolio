import Link from "next/link"

import { Container } from "@/components/shared/container"
import { Button } from "@/components/ui/button"

export default function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center">
      <Container>
        <div className="mx-auto max-w-xl text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
            404 error
          </p>

          <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-6xl">
            This page could not be found
          </h1>

          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            The page may have moved, been removed, or never existed.
          </p>

          <div className="mt-8">
            <Button asChild>
              <Link href="/">Return home</Link>
            </Button>
          </div>
        </div>
      </Container>
    </main>
  )
}