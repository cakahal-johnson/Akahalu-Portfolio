import Link from "next/link"

import { Container } from "@/components/shared/container"
import { siteConfig } from "@/config/site"

function SiteFooter() {
  const currentYear = new Date().getFullYear()

  return (
    <footer className="border-t border-border/60">
      <Container className="flex flex-col gap-6 py-8 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="font-medium">{siteConfig.name}</p>

          <p className="mt-1 text-sm text-muted-foreground">
            Building secure, thoughtful, and scalable digital products.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {siteConfig.navigation.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-muted-foreground transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </div>

        <p className="text-sm text-muted-foreground">
          © {currentYear} {siteConfig.shortName}
        </p>
      </Container>
    </footer>
  )
}

export { SiteFooter }