import { AdminMobileNav } from "@/components/admin/layout/admin-mobile-nav"
import { AdminUserMenu } from "@/components/admin/layout/admin-user-menu"

export function AdminHeader() {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-border bg-background/95 px-4 backdrop-blur sm:px-6 lg:px-8">
      <AdminMobileNav />

      <div className="hidden lg:block">
        <p className="text-sm font-medium">
          Portfolio administration
        </p>

        <p className="text-xs text-muted-foreground">
          Manage your public portfolio
        </p>
      </div>

      <AdminUserMenu />
    </header>
  )
}