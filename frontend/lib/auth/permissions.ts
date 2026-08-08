import type {
  AuthenticatedUser,
} from "@/types/authentication"

export function getUserPermissionCodes(
  user: AuthenticatedUser
): Set<string> {
  const permissions =
    new Set<string>()

  for (const role of user.roles) {
    if (
      !role.is_active ||
      role.deleted_at !== null
    ) {
      continue
    }

    for (const permission of role.permissions) {
      if (
        !permission.is_active ||
        permission.deleted_at !== null
      ) {
        continue
      }

      permissions.add(
        permission.code
          .trim()
          .toLowerCase()
      )
    }
  }

  return permissions
}

export function userHasPermission(
  user: AuthenticatedUser,
  permissionCode: string
): boolean {
  if (user.is_superuser) {
    return true
  }

  return getUserPermissionCodes(
    user
  ).has(
    permissionCode
      .trim()
      .toLowerCase()
  )
}