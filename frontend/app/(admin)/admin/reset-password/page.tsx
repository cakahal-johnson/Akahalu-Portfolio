import type { Metadata } from "next"
import Link from "next/link"

import { ResetPasswordForm } from "@/components/admin/auth/reset-password-form"
import { siteConfig } from "@/config/site"

export const metadata: Metadata = {
  title: "Reset Admin Password",
  description:
    "Choose a new password for the Akahalu Portfolio administration account.",
  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminResetPasswordPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/20 px-4 py-12 sm:px-6">
      <div className="w-full">
        <div className="mx-auto mb-8 max-w-md text-center">
          <Link
            href="/"
            className="text-lg font-bold tracking-tight"
          >
            {siteConfig.name}
          </Link>

          <p className="mt-2 text-xs uppercase tracking-[0.2em] text-muted-foreground">
            Administration
          </p>
        </div>

        <div className="mx-auto flex justify-center">
          <ResetPasswordForm />
        </div>
      </div>
    </main>
  )
}