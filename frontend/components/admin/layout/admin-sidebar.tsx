"use client"

import {
  ExternalLink,
} from "lucide-react"
import Link from "next/link"
import {
  usePathname,
} from "next/navigation"

import { useAdminSession } from "@/components/admin/auth/admin-session-context"
import { adminNavigation } from "@/config/admin-navigation"
import { siteConfig } from "@/config/site"
import { userHasPermission } from "@/lib/auth/permissions"
import { cn } from "@/lib/utils"

function isActiveRoute(
  pathname: string,
  href: string
): boolean {
  if (href === "/admin") {
    return pathname === href
  }

  return (
    pathname === href ||
    pathname.startsWith(
      `${href}/`
    )
  )
}

export function AdminSidebar() {
  const pathname =
    usePathname()

  const { user } =
    useAdminSession()

  const navigation =
    adminNavigation.filter(
      (item) => {
        if (
          item.superuserOnly &&
          !user.is_superuser
        ) {
          return false
        }

        if (!item.permission) {
          return true
        }

        return userHasPermission(
          user,
          item.permission
        )
      }
    )

  return (
    <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r border-border bg-background lg:flex lg:flex-col">
      <div className="flex h-16 items-center border-b border-border px-6">
        <Link
          href="/admin"
          className="min-w-0"
        >
          <p className="truncate font-bold tracking-tight">
            {siteConfig.name}
          </p>

          <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
            Administration
          </p>
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {navigation.map(
            (item) => {
              const active =
                isActiveRoute(
                  pathname,
                  item.href
                )

              const Icon =
                item.icon

              return (
                <Link
                  key={
                    item.href
                  }
                  href={
                    item.href
                  }
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <Icon
                    className="size-4"
                    aria-hidden="true"
                  />

                  {item.title}
                </Link>
              )
            }
          )}
        </div>
      </nav>

      <div className="border-t border-border p-4">
        <Link
          href="/"
          target="_blank"
          className="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <ExternalLink
            className="size-4"
            aria-hidden="true"
          />

          View portfolio
        </Link>
      </div>
    </aside>
  )
}