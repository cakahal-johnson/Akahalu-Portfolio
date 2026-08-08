"use client"

import {
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  LogIn,
  Mail,
} from "lucide-react"
import Link from "next/link"
import {
  useRouter,
} from "next/navigation"
import {
  useState,
  type FormEvent,
} from "react"

import { Button } from "@/components/ui/button"
import {
  ADMIN_HOME_PATH,
} from "@/lib/auth/constants"
import {
  AdminAuthenticationError,
  adminAuthenticationService,
} from "@/services/authentication"

export function AdminLoginForm() {
  const router = useRouter()

  const [
    email,
    setEmail,
  ] = useState("")

  const [
    password,
    setPassword,
  ] = useState("")

  const [
    showPassword,
    setShowPassword,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )

  const [
    isSubmitting,
    setIsSubmitting,
  ] = useState(false)

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setError(null)

    const normalizedEmail =
      email.trim().toLowerCase()

    if (!normalizedEmail) {
      setError(
        "Enter your administrator email address."
      )

      return
    }

    if (!password) {
      setError(
        "Enter your password."
      )

      return
    }

    try {
      setIsSubmitting(true)

      await adminAuthenticationService.login(
        {
          email:
            normalizedEmail,
          password,
        }
      )

      setPassword("")

      router.replace(
        ADMIN_HOME_PATH
      )

      router.refresh()
    } catch (caughtError) {
      if (
        caughtError instanceof
        AdminAuthenticationError
      ) {
        setError(
          caughtError.message
        )

        return
      }

      setError(
        "Sign-in could not be completed. Please try again."
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-md rounded-3xl border border-border/70 bg-card p-6 shadow-sm sm:p-8">
      <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <LockKeyhole
          className="size-6"
          aria-hidden="true"
        />
      </div>

      <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
        Administrator sign in
      </h1>

      <p className="mt-3 text-sm leading-6 text-muted-foreground">
        Sign in to manage portfolio
        content, projects, experience,
        users, and inquiries.
      </p>

      {error ? (
        <div
          className="mt-6 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      <form
        className="mt-7"
        onSubmit={handleSubmit}
        noValidate
      >
        <div>
          <label
            htmlFor="admin-login-email"
            className="text-sm font-medium"
          >
            Email
          </label>

          <div className="relative mt-2">
            <Mail
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />

            <input
              id="admin-login-email"
              name="email"
              type="email"
              autoComplete="username"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
              className="h-11 w-full rounded-lg border border-input bg-background pl-10 pr-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="admin@example.com"
            />
          </div>
        </div>

        <div className="mt-5">
          <div className="flex items-center justify-between gap-4">
            <label
              htmlFor="admin-login-password"
              className="text-sm font-medium"
            >
              Password
            </label>

            <Link
              href="/admin/forgot-password"
              className="text-sm font-medium text-primary hover:underline"
            >
              Forgot password?
            </Link>
          </div>

          <div className="relative mt-2">
            <input
              id="admin-login-password"
              name="password"
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              autoComplete="current-password"
              maxLength={128}
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              className="h-11 w-full rounded-lg border border-input bg-background px-3 pr-11 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword(
                  (value) =>
                    !value
                )
              }
              className="absolute right-0 top-0 flex size-11 items-center justify-center text-muted-foreground transition-colors hover:text-foreground"
              aria-label={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
            >
              {showPassword ? (
                <EyeOff
                  className="size-4"
                  aria-hidden="true"
                />
              ) : (
                <Eye
                  className="size-4"
                  aria-hidden="true"
                />
              )}
            </button>
          </div>
        </div>

        <Button
          type="submit"
          size="lg"
          className="mt-7 w-full"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2
                className="animate-spin"
                aria-hidden="true"
              />

              Signing in...
            </>
          ) : (
            <>
              Sign in

              <LogIn
                aria-hidden="true"
              />
            </>
          )}
        </Button>
      </form>

      <p className="mt-6 text-center text-xs leading-5 text-muted-foreground">
        Authorized portfolio management
        accounts only.
      </p>
    </div>
  )
}