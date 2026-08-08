"use client"

import {
  CheckCircle2,
  Eye,
  EyeOff,
  KeyRound,
  Loader2,
  ShieldCheck,
} from "lucide-react"
import Link from "next/link"
import {
  useState,
  useSyncExternalStore,
  type FormEvent,
} from "react"

import { Button } from "@/components/ui/button"
import { isApiError } from "@/lib/api"
import {
  ADMIN_PASSWORD_RESET_EXPIRY_KEY,
  ADMIN_PASSWORD_RESET_TOKEN_KEY,
} from "@/lib/auth/constants"
import { publicAccountService } from "@/services/account"

function subscribeToResetSession(): () => void {
  return () => undefined
}

function getResetTokenSnapshot(): string | null {
  if (typeof window === "undefined") {
    return null
  }

  const storedToken =
    window.sessionStorage.getItem(
      ADMIN_PASSWORD_RESET_TOKEN_KEY
    )

  if (!storedToken) {
    return null
  }

  const storedExpiry =
    window.sessionStorage.getItem(
      ADMIN_PASSWORD_RESET_EXPIRY_KEY
    )

  if (!storedExpiry) {
    return storedToken
  }

  const expiry =
    new Date(storedExpiry)

  if (
    Number.isNaN(
      expiry.getTime()
    )
  ) {
    return storedToken
  }

  if (
    expiry.getTime() <=
    Date.now()
  ) {
    return null
  }

  return storedToken
}

function getServerResetTokenSnapshot(): null {
  return null
}

function getHydratedSnapshot(): boolean {
  return true
}

function getServerHydratedSnapshot(): boolean {
  return false
}

export function ResetPasswordForm() {
  const token =
    useSyncExternalStore(
      subscribeToResetSession,
      getResetTokenSnapshot,
      getServerResetTokenSnapshot
    )

  const tokenLoaded =
    useSyncExternalStore(
      subscribeToResetSession,
      getHydratedSnapshot,
      getServerHydratedSnapshot
    )

  const [
    password,
    setPassword,
  ] = useState("")

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("")

  const [
    showPassword,
    setShowPassword,
  ] = useState(false)

  const [
    showConfirmation,
    setShowConfirmation,
  ] = useState(false)

  const [
    fieldError,
    setFieldError,
  ] = useState<string | null>(
    null
  )

  const [
    submitError,
    setSubmitError,
  ] = useState<string | null>(
    null
  )

  const [
    successMessage,
    setSuccessMessage,
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

    if (
      isSubmitting ||
      !token
    ) {
      return
    }

    setFieldError(null)
    setSubmitError(null)

    if (password.length < 12) {
      setFieldError(
        "Password must contain at least 12 characters."
      )

      return
    }

    if (password.length > 128) {
      setFieldError(
        "Password cannot exceed 128 characters."
      )

      return
    }

    if (
      password !==
      confirmPassword
    ) {
      setFieldError(
        "The passwords do not match."
      )

      return
    }

    try {
      setIsSubmitting(true)

      const response =
        await publicAccountService.resetPassword(
          {
            token,
            new_password: password,
          }
        )

      window.sessionStorage.removeItem(
        ADMIN_PASSWORD_RESET_TOKEN_KEY
      )

      window.sessionStorage.removeItem(
        ADMIN_PASSWORD_RESET_EXPIRY_KEY
      )

      setPassword("")
      setConfirmPassword("")
      setSuccessMessage(
        response.message
      )
    } catch (error) {
      if (isApiError(error)) {
        setSubmitError(
          error.isNetworkError
            ? "The API could not be reached. Check that the backend is running and try again."
            : error.message
        )

        return
      }

      setSubmitError(
        "The password could not be reset. Please try again."
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (!tokenLoaded) {
    return (
      <div className="flex items-center gap-3 text-sm text-muted-foreground">
        <Loader2
          className="size-4 animate-spin"
          aria-hidden="true"
        />

        Loading password recovery...
      </div>
    )
  }

  if (!token) {
    return (
      <div className="w-full max-w-md rounded-3xl border border-border/70 bg-card p-6 shadow-sm sm:p-8">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground">
          <KeyRound
            className="size-6"
            aria-hidden="true"
          />
        </div>

        <h1 className="mt-6 text-2xl font-bold tracking-tight">
          Reset session unavailable
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          This reset session is missing or
          has expired. Start a new password
          recovery request.
        </p>

        <Button
          asChild
          className="mt-6 w-full"
        >
          <Link href="/admin/forgot-password">
            Start password recovery
          </Link>
        </Button>
      </div>
    )
  }

  if (successMessage) {
    return (
      <div className="w-full max-w-md rounded-3xl border border-border/70 bg-card p-6 shadow-sm sm:p-8">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <CheckCircle2
            className="size-6"
            aria-hidden="true"
          />
        </div>

        <h1 className="mt-6 text-2xl font-bold tracking-tight">
          Password updated
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          {successMessage}
        </p>

        <p className="mt-4 text-sm leading-6 text-muted-foreground">
          Existing authentication sessions
          and refresh tokens have been revoked.
          Your administrator account is ready
          for a fresh sign-in.
        </p>

        <div className="mt-6 rounded-xl bg-muted/50 p-4 text-sm leading-6 text-muted-foreground">
          The administrator sign-in page is
          the next phase of the admin frontend.
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md">
      <div className="rounded-3xl border border-border/70 bg-card p-6 shadow-sm sm:p-8">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <ShieldCheck
            className="size-6"
            aria-hidden="true"
          />
        </div>

        <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
          Choose a new password
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Use at least 12 characters. Your
          previous sessions will no longer be
          valid after the reset.
        </p>

        {submitError ? (
          <div
            className="mt-6 rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
            role="alert"
          >
            {submitError}
          </div>
        ) : null}

        <form
          className="mt-7"
          onSubmit={handleSubmit}
          noValidate
        >
          <div>
            <label
              htmlFor="admin-new-password"
              className="text-sm font-medium"
            >
              New password
            </label>

            <div className="relative mt-2">
              <input
                id="admin-new-password"
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                name="password"
                autoComplete="new-password"
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value
                  )
                }
                minLength={12}
                maxLength={128}
                aria-invalid={
                  Boolean(fieldError)
                }
                className="h-11 w-full rounded-lg border border-input bg-background px-3 pr-11 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              />

              <button
                type="button"
                onClick={() =>
                  setShowPassword(
                    (value) => !value
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

          <div className="mt-5">
            <label
              htmlFor="admin-confirm-password"
              className="text-sm font-medium"
            >
              Confirm password
            </label>

            <div className="relative mt-2">
              <input
                id="admin-confirm-password"
                type={
                  showConfirmation
                    ? "text"
                    : "password"
                }
                name="confirm_password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(event) =>
                  setConfirmPassword(
                    event.target.value
                  )
                }
                minLength={12}
                maxLength={128}
                aria-invalid={
                  Boolean(fieldError)
                }
                className="h-11 w-full rounded-lg border border-input bg-background px-3 pr-11 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              />

              <button
                type="button"
                onClick={() =>
                  setShowConfirmation(
                    (value) => !value
                  )
                }
                className="absolute right-0 top-0 flex size-11 items-center justify-center text-muted-foreground transition-colors hover:text-foreground"
                aria-label={
                  showConfirmation
                    ? "Hide confirmation password"
                    : "Show confirmation password"
                }
              >
                {showConfirmation ? (
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

          {fieldError ? (
            <p
              className="mt-3 text-sm text-destructive"
              role="alert"
            >
              {fieldError}
            </p>
          ) : null}

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

                Updating password...
              </>
            ) : (
              <>
                Update password

                <KeyRound
                  aria-hidden="true"
                />
              </>
            )}
          </Button>
        </form>
      </div>
    </div>
  )
}