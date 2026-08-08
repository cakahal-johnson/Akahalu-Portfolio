import { AdminHeader } from "@/components/admin/layout/admin-header"
import { AdminSidebar } from "@/components/admin/layout/admin-sidebar"

type AdminShellProps = {
  children: React.ReactNode
}

export function AdminShell({
  children,
}: AdminShellProps) {
  return (
    <div className="min-h-screen bg-muted/20">
      <AdminSidebar />

      <div className="min-h-screen lg:pl-72">
        <AdminHeader />

        <main className="p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  )
}