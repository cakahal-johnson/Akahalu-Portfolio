import type { ReactNode } from "react"

import { SiteFooter } from "@/components/layout/site-footer"
import { SiteHeader } from "@/components/layout/site-header"

type SiteLayoutProps = {
  children: ReactNode
}

export default function SiteLayout({
  children,
}: SiteLayoutProps) {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />

      <main className="flex-1">{children}</main>

      <SiteFooter />
    </div>
  )
}