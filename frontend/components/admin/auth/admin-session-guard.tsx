"use client"

import {
  Loader2,
} from "lucide-react"
import {
  useRouter,
} from "next/navigation"
import {
  useEffect,
  useState,
} from "react"

import { AdminSessionProvider } from "@/components/admin/auth/admin-session-context"
import {
  ADMIN_LOGIN_PATH,
} from "@/lib/auth/constants"
import {
  AdminAuthenticationError,
  adminAuthenticationService,
} from "@/services/authentication"

import type {
  AuthenticatedUser,
} from "@/types/authentication"

type AdminSessionGuardProps = {
  children: React.ReactNode
}

export function AdminSessionGuard({
  children,
}: AdminSessionGuardProps) {
  const router = useRouter()

  const [
    user,
    setUser,
  ] =
    useState<AuthenticatedUser | null>(
      null
    )

  const [
    loading,
    setLoading,
  ] = useState(true)

  useEffect(() => {
    let cancelled = false

    async function loadSession() {
      try {
        const session =
          await adminAuthenticationService.getSession()

        if (!cancelled) {
          setUser(
            session.user
          )
        }
      } catch (error) {
        if (cancelled) {
          return
        }

        if (
          error instanceof
          AdminAuthenticationError ||
          error instanceof Error
        ) {
          router.replace(
            ADMIN_LOGIN_PATH
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadSession()

    return () => {
      cancelled = true
    }
  }, [router])

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2
            className="size-7 animate-spin text-primary"
            aria-hidden="true"
          />

          <p className="text-sm text-muted-foreground">
            Loading administration...
          </p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <AdminSessionProvider
      user={user}
    >
      {children}
    </AdminSessionProvider>
  )
}