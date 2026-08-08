import { AdminSessionGuard } from "@/components/admin/auth/admin-session-guard"
import { AdminShell } from "@/components/admin/layout/admin-shell"

type ProtectedAdminLayoutProps = Readonly<{
  children: React.ReactNode
}>

export default function ProtectedAdminLayout({
  children,
}: ProtectedAdminLayoutProps) {
  return (
    <AdminSessionGuard>
      <AdminShell>
        {children}
      </AdminShell>
    </AdminSessionGuard>
  )
}