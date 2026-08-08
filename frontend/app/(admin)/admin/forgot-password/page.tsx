import type { Metadata } from "next"
import Link from "next/link"

import { ForgotPasswordForm } from "@/components/admin/auth/forgot-password-form"
import { siteConfig } from "@/config/site"

export const metadata: Metadata = {
  title: "Recover Admin Access",
  description:
    "Recover access to the Akahalu Portfolio administration area.",
  robots: {
    index: false,
    follow: false,
  },
}

export default function AdminForgotPasswordPage() {
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
          <ForgotPasswordForm />
        </div>

        <p className="mx-auto mt-8 max-w-md text-center text-xs leading-5 text-muted-foreground">
          Administrator recovery is intended
          only for authorized portfolio
          management accounts.
        </p>
      </div>
    </main>
  )
}