"use client"

import {
  ExternalLink,
  Menu,
  X,
} from "lucide-react"
import Link from "next/link"
import {
  usePathname,
} from "next/navigation"
import {
  useState,
} from "react"
import {
  createPortal,
} from "react-dom"

import { useAdminSession } from "@/components/admin/auth/admin-session-context"
import { adminNavigation } from "@/config/admin-navigation"
import { siteConfig } from "@/config/site"
import { userHasPermission } from "@/lib/auth/permissions"
import { cn } from "@/lib/utils"

export function AdminMobileNav() {
  const pathname =
    usePathname()

  const { user } =
    useAdminSession()

  const [
    open,
    setOpen,
  ] = useState(false)

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

  function isActive(
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

  function closeNavigation(): void {
    setOpen(false)
  }

  const drawer =
    open &&
    typeof document !== "undefined"
      ? createPortal(
          <div className="fixed inset-0 z-[9999] lg:hidden">
            <button
              type="button"
              className="absolute inset-0 bg-black/55 backdrop-blur-[1px]"
              onClick={closeNavigation}
              aria-label="Close admin navigation"
            />

            <aside
              className="absolute inset-y-0 left-0 z-10 flex w-[min(86vw,320px)] flex-col border-r border-border bg-background shadow-2xl"
              aria-label="Admin navigation"
            >
              <div className="flex h-16 shrink-0 items-center justify-between border-b border-border px-5">
                <Link
                  href="/admin"
                  onClick={closeNavigation}
                  className="min-w-0"
                >
                  <p className="truncate font-bold">
                    {siteConfig.name}
                  </p>

                  <p className="text-xs uppercase tracking-[0.16em] text-muted-foreground">
                    Administration
                  </p>
                </Link>

                <button
                  type="button"
                  onClick={closeNavigation}
                  className="inline-flex size-10 shrink-0 items-center justify-center rounded-lg transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  aria-label="Close admin navigation"
                >
                  <X
                    className="size-5"
                    aria-hidden="true"
                  />
                </button>
              </div>

              <nav className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-4">
                <div className="space-y-1">
                  {navigation.map(
                    (item) => {
                      const Icon =
                        item.icon

                      const active =
                        isActive(
                          item.href
                        )

                      return (
                        <Link
                          key={
                            item.href
                          }
                          href={
                            item.href
                          }
                          onClick={
                            closeNavigation
                          }
                          aria-current={
                            active
                              ? "page"
                              : undefined
                          }
                          className={cn(
                            "flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-colors",
                            active
                              ? "bg-primary text-primary-foreground"
                              : "text-muted-foreground hover:bg-muted hover:text-foreground"
                          )}
                        >
                          <Icon
                            className="size-4 shrink-0"
                            aria-hidden="true"
                          />

                          <span>
                            {item.title}
                          </span>
                        </Link>
                      )
                    }
                  )}
                </div>
              </nav>

              <div className="shrink-0 border-t border-border p-4">
                <Link
                  href="/"
                  target="_blank"
                  rel="noreferrer"
                  onClick={
                    closeNavigation
                  }
                  className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
                >
                  <ExternalLink
                    className="size-4 shrink-0"
                    aria-hidden="true"
                  />

                  View portfolio
                </Link>
              </div>
            </aside>
          </div>,
          document.body
        )
      : null

  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="inline-flex size-10 items-center justify-center rounded-lg border border-border bg-background transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring lg:hidden"
        aria-label="Open admin navigation"
        aria-expanded={open}
        aria-haspopup="dialog"
      >
        <Menu
          className="size-5"
          aria-hidden="true"
        />
      </button>

      {drawer}
    </>
  )
}