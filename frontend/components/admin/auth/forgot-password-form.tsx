"use client"

import {
  ArrowRight,
  KeyRound,
  Loader2,
  Mail,
} from "lucide-react"
import { useRouter } from "next/navigation"
import {
  useState,
  type FormEvent,
} from "react"

import { Button } from "@/components/ui/button"
import { isApiError } from "@/lib/api"
import {
  ADMIN_PASSWORD_RESET_EXPIRY_KEY,
  ADMIN_PASSWORD_RESET_TOKEN_KEY,
} from "@/lib/auth/constants"
import { publicAccountService } from "@/services/account"

export function ForgotPasswordForm() {
  const router = useRouter()

  const [
    email,
    setEmail,
  ] = useState("")

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
    message,
    setMessage,
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

    setFieldError(null)
    setSubmitError(null)
    setMessage(null)

    const normalizedEmail =
      email.trim().toLowerCase()

    if (!normalizedEmail) {
      setFieldError(
        "Enter your administrator email address."
      )

      return
    }

    if (
      !normalizedEmail.includes("@")
    ) {
      setFieldError(
        "Enter a valid email address."
      )

      return
    }

    try {
      setIsSubmitting(true)

      const response =
        await publicAccountService.forgotPassword(
          {
            email: normalizedEmail,
          }
        )

      /*
       * Development behaviour:
       * FastAPI currently returns the raw reset
       * token until email delivery is implemented.
       *
       * Keep it only for this browser tab.
       */
      if (response.reset_token) {
        sessionStorage.setItem(
          ADMIN_PASSWORD_RESET_TOKEN_KEY,
          response.reset_token
        )

        if (
          response.reset_token_expires_at
        ) {
          sessionStorage.setItem(
            ADMIN_PASSWORD_RESET_EXPIRY_KEY,
            response.reset_token_expires_at
          )
        } else {
          sessionStorage.removeItem(
            ADMIN_PASSWORD_RESET_EXPIRY_KEY
          )
        }

        router.push(
          "/admin/reset-password"
        )

        return
      }

      /*
       * Production-ready fallback:
       * once email delivery replaces token
       * exposure, the generic backend message
       * is shown instead.
       */
      setMessage(
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
        "Password recovery could not be started. Please try again."
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="w-full max-w-md">
      <div className="rounded-3xl border border-border/70 bg-card p-6 shadow-sm sm:p-8">
        <div className="flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <KeyRound
            className="size-6"
            aria-hidden="true"
          />
        </div>

        <h1 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
          Recover administrator access
        </h1>

        <p className="mt-3 text-sm leading-6 text-muted-foreground">
          Enter the email address associated
          with your administrator account.
        </p>

        {message ? (
          <div
            className="mt-6 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm leading-6"
            role="status"
          >
            {message}
          </div>
        ) : null}

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
          <label
            htmlFor="admin-recovery-email"
            className="text-sm font-medium"
          >
            Administrator email
          </label>

          <div className="relative mt-2">
            <Mail
              className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
              aria-hidden="true"
            />

            <input
              id="admin-recovery-email"
              type="email"
              name="email"
              autoComplete="email"
              value={email}
              onChange={(event) =>
                setEmail(
                  event.target.value
                )
              }
              aria-invalid={
                Boolean(fieldError)
              }
              className="h-11 w-full rounded-lg border border-input bg-background pl-10 pr-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="admin@example.com"
            />
          </div>

          {fieldError ? (
            <p
              className="mt-2 text-sm text-destructive"
              role="alert"
            >
              {fieldError}
            </p>
          ) : null}

          <Button
            type="submit"
            size="lg"
            className="mt-6 w-full"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2
                  className="animate-spin"
                  aria-hidden="true"
                />

                Preparing reset...
              </>
            ) : (
              <>
                Continue

                <ArrowRight
                  aria-hidden="true"
                />
              </>
            )}
          </Button>
        </form>

        <p className="mt-6 text-center text-xs leading-5 text-muted-foreground">
          For security, the response does not
          reveal whether an account exists for
          an arbitrary email address.
        </p>
      </div>
    </div>
  )
}