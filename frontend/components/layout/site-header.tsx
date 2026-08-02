import Link from "next/link"

import { MobileNavigation } from "@/components/layout/mobile-navigation"
import { Container } from "@/components/shared/container"
import { Button } from "@/components/ui/button"
import { siteConfig } from "@/config/site"

function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-border/60 bg-background/90 backdrop-blur">
      <Container className="flex h-16 items-center justify-between gap-4">
        <Link
          href="/"
          className="inline-flex min-w-0 items-center gap-2 font-semibold tracking-tight"
          aria-label={`${siteConfig.name} homepage`}
        >
          <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
            {siteConfig.initials}
          </span>

          <span className="truncate">
            {siteConfig.shortName}
          </span>
        </Link>

        <nav
          className="hidden items-center gap-6 md:flex"
          aria-label="Primary navigation"
        >
          {siteConfig.navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Button
            asChild
            className="hidden md:inline-flex"
          >
            <Link href="/contact">
              Let&apos;s talk
            </Link>
          </Button>

          <MobileNavigation />
        </div>
      </Container>
    </header>
  )
}

export { SiteHeader }