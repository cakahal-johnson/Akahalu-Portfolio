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
        if (
          !cancelled &&
          (error instanceof
            AdminAuthenticationError ||
            error instanceof Error)
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
      <div className="flex min-h-screen items-center justify-center">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2
            className="size-5 animate-spin"
            aria-hidden="true"
          />

          Loading administration...
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return children
}