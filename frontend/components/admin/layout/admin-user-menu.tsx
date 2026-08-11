"use client"

import {
  AdminLogoutButton,
} from "@/components/admin/auth/admin-logout-button"

import {
  useAdminSession,
} from "@/components/admin/auth/admin-session-context"

export function AdminUserMenu() {
  const {
    user,
  } =
    useAdminSession()

  const initials =
    `${user.first_name.charAt(
      0
    )}${user.last_name.charAt(
      0
    )}`.toUpperCase()

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

      <AdminLogoutButton
        compact
      />
    </div>
  )
}