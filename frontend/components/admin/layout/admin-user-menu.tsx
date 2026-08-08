"use client"

import {
  LogOut,
} from "lucide-react"
import {
  useRouter,
} from "next/navigation"
import {
  useState,
} from "react"

import { useAdminSession } from "@/components/admin/auth/admin-session-context"
import { Button } from "@/components/ui/button"
import {
  ADMIN_LOGIN_PATH,
} from "@/lib/auth/constants"
import { adminAuthenticationService } from "@/services/authentication"

export function AdminUserMenu() {
  const router =
    useRouter()

  const { user } =
    useAdminSession()

  const [
    loggingOut,
    setLoggingOut,
  ] = useState(false)

  async function logout() {
    if (loggingOut) {
      return
    }

    try {
      setLoggingOut(true)

      await adminAuthenticationService.logout()
    } finally {
      router.replace(
        ADMIN_LOGIN_PATH
      )

      router.refresh()
    }
  }

  const initials =
    `${user.first_name.charAt(0)}${user.last_name.charAt(0)}`
      .toUpperCase()

  return (
    <div className="flex items-center gap-3">
      <div className="hidden text-right sm:block">
        <p className="max-w-48 truncate text-sm font-medium">
          {user.display_name ??
            `${user.first_name} ${user.last_name}`}
        </p>

        <p className="max-w-48 truncate text-xs text-muted-foreground">
          {user.email}
        </p>
      </div>

      <div className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
        {initials}
      </div>

      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={logout}
        disabled={loggingOut}
        aria-label="Sign out"
      >
        <LogOut
          className="size-4"
          aria-hidden="true"
        />
      </Button>
    </div>
  )
}