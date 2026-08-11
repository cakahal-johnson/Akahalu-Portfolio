"use client"

import {
  Loader2,
  LogOut,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  ADMIN_LOGIN_PATH,
} from "@/lib/auth/constants"

import {
  cn,
} from "@/lib/utils"

import {
  AdminAuthenticationError,
  adminAuthenticationService,
} from "@/services/authentication"

type AdminLogoutButtonProps = {
  compact?: boolean

  className?: string

  onLoggedOut?: () => void
}

export function AdminLogoutButton({
  compact = false,
  className,
  onLoggedOut,
}: AdminLogoutButtonProps) {
  const [
    loggingOut,
    setLoggingOut,
  ] =
    useState(
      false
    )

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  async function logout() {
    if (
      loggingOut
    ) {
      return
    }

    setLoggingOut(
      true
    )

    setError(
      null
    )

    try {
      await adminAuthenticationService.logout()

      onLoggedOut?.()

      /*
       * A full navigation guarantees that
       * all protected client state is
       * discarded after logout.
       */
      window.location.assign(
        ADMIN_LOGIN_PATH
      )
    } catch (
      caughtError
    ) {
      setError(
        caughtError instanceof
        AdminAuthenticationError
          ? caughtError.message
          : "Sign out could not be completed."
      )

      setLoggingOut(
        false
      )
    }
  }

  if (
    compact
  ) {
    return (
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={() => {
          void logout()
        }}
        disabled={
          loggingOut
        }
        aria-label="Sign out"
        title={
          error ??
          "Sign out"
        }
        className={
          className
        }
      >
        {loggingOut ? (
          <Loader2
            className="size-4 animate-spin"
            aria-hidden="true"
          />
        ) : (
          <LogOut
            className="size-4"
            aria-hidden="true"
          />
        )}
      </Button>
    )
  }

  return (
    <div className="w-full">
      <Button
        type="button"
        variant="ghost"
        onClick={() => {
          void logout()
        }}
        disabled={
          loggingOut
        }
        className={cn(
          "w-full justify-start gap-3 px-3",
          className
        )}
      >
        {loggingOut ? (
          <Loader2
            className="size-4 animate-spin"
            aria-hidden="true"
          />
        ) : (
          <LogOut
            className="size-4"
            aria-hidden="true"
          />
        )}

        {loggingOut
          ? "Signing out..."
          : "Sign out"}
      </Button>

      {error ? (
        <p
          role="alert"
          className="mt-1 px-3 text-xs leading-5 text-destructive"
        >
          {error}
        </p>
      ) : null}
    </div>
  )
}