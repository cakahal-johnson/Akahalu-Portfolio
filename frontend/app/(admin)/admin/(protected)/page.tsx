import Link from "next/link"

import { Button } from "@/components/ui/button"

export default function AdminDashboardPage() {
  return (
    <main className="min-h-screen bg-muted/20 px-4 py-12 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Administration
        </p>

        <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
          Portfolio dashboard
        </h1>

        <p className="mt-4 max-w-2xl leading-7 text-muted-foreground">
          Authentication is active. The
          dashboard navigation and portfolio
          management modules will be added in
          the next phase.
        </p>

        <div className="mt-8">
          <Button
            asChild
            variant="outline"
          >
            <Link href="/">
              View public portfolio
            </Link>
          </Button>
        </div>
      </div>
    </main>
  )
}