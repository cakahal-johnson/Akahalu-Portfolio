import { AdminSessionGuard } from "@/components/admin/auth/admin-session-guard"

type ProtectedAdminLayoutProps = Readonly<{
  children: React.ReactNode
}>

export default function ProtectedAdminLayout({
  children,
}: ProtectedAdminLayoutProps) {
  return (
    <AdminSessionGuard>
      {children}
    </AdminSessionGuard>
  )
}