"use client"

import {
  CheckCircle2,
  Loader2,
  Send,
} from "lucide-react"
import {
  useState,
  type FormEvent,
} from "react"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import { isApiError } from "@/lib/api"
import { publicContactService } from "@/services/contact"

import type {
  ContactInquiryPublicCreate,
  ContactInquiryType,
} from "@/types/contact"

const inquiryTypeValues = [
  "general",
  "employment",
  "freelance",
  "contract",
  "collaboration",
  "project",
  "support",
  "other",
] as const satisfies readonly ContactInquiryType[]

const contactFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(
      2,
      "Please enter at least 2 characters."
    )
    .max(
      150,
      "Name cannot exceed 150 characters."
    ),

  email: z
    .string()
    .trim()
    .email(
      "Please enter a valid email address."
    ),

  phone: z
    .string()
    .trim()
    .max(
      40,
      "Phone number cannot exceed 40 characters."
    )
    .optional(),

  company: z
    .string()
    .trim()
    .max(
      150,
      "Company cannot exceed 150 characters."
    )
    .optional(),

  inquiryType: z.enum(
    inquiryTypeValues
  ),

  subject: z
    .string()
    .trim()
    .min(
      3,
      "Subject must contain at least 3 characters."
    )
    .max(
      200,
      "Subject cannot exceed 200 characters."
    ),

  message: z
    .string()
    .trim()
    .min(
      10,
      "Message must contain at least 10 characters."
    )
    .max(
      10_000,
      "Message cannot exceed 10,000 characters."
    ),

  consent: z.literal(
    true,
    {
      error:
        "Please confirm that I may use these details to respond to your inquiry.",
    }
  ),

  website: z
    .string()
    .trim()
    .max(200)
    .optional(),
})

type FormField =
  | "name"
  | "email"
  | "phone"
  | "company"
  | "inquiryType"
  | "subject"
  | "message"
  | "consent"

type FieldErrors = Partial<
  Record<FormField, string>
>

const inquiryTypeOptions: ReadonlyArray<{
  value: ContactInquiryType
  label: string
}> = [
  {
    value: "general",
    label: "General inquiry",
  },
  {
    value: "employment",
    label: "Employment opportunity",
  },
  {
    value: "freelance",
    label: "Freelance work",
  },
  {
    value: "contract",
    label: "Contract opportunity",
  },
  {
    value: "collaboration",
    label: "Collaboration",
  },
  {
    value: "project",
    label: "Project discussion",
  },
  {
    value: "support",
    label: "Support",
  },
  {
    value: "other",
    label: "Other",
  },
]

function getStringValue(
  formData: FormData,
  key: string
): string {
  const value =
    formData.get(key)

  return typeof value === "string"
    ? value
    : ""
}

function buildFieldErrors(
  issues: z.ZodIssue[]
): FieldErrors {
  const errors: FieldErrors = {}

  for (const issue of issues) {
    const field =
      issue.path[0]

    if (
      typeof field !== "string"
    ) {
      continue
    }

    if (
      field === "inquiryType" ||
      field === "consent" ||
      field === "name" ||
      field === "email" ||
      field === "phone" ||
      field === "company" ||
      field === "subject" ||
      field === "message"
    ) {
      if (!errors[field]) {
        errors[field] =
          issue.message
      }
    }
  }

  return errors
}

function FieldError({
  message,
}: {
  message?: string
}) {
  if (!message) {
    return null
  }

  return (
    <p
      className="mt-1.5 text-sm text-destructive"
      role="alert"
    >
      {message}
    </p>
  )
}

export function ContactForm() {
  const [
    fieldErrors,
    setFieldErrors,
  ] = useState<FieldErrors>({})

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

    if (isSubmitting) {
      return
    }

    setFieldErrors({})
    setSubmitError(null)
    setSuccessMessage(null)

    const form =
      event.currentTarget

    const formData =
      new FormData(form)

    const result =
      contactFormSchema.safeParse({
        name:
          getStringValue(
            formData,
            "name"
          ),

        email:
          getStringValue(
            formData,
            "email"
          ),

        phone:
          getStringValue(
            formData,
            "phone"
          ),

        company:
          getStringValue(
            formData,
            "company"
          ),

        inquiryType:
          getStringValue(
            formData,
            "inquiry_type"
          ),

        subject:
          getStringValue(
            formData,
            "subject"
          ),

        message:
          getStringValue(
            formData,
            "message"
          ),

        consent:
          formData.get(
            "consent"
          ) === "on",

        website:
          getStringValue(
            formData,
            "website"
          ),
      })

    if (!result.success) {
      setFieldErrors(
        buildFieldErrors(
          result.error.issues
        )
      )

      return
    }

    const {
      inquiryType,
      consent,
      website,
      ...values
    } = result.data

    const payload: ContactInquiryPublicCreate = {
      name: values.name,
      email: values.email.toLowerCase(),

      phone:
        values.phone || null,

      company:
        values.company || null,

      subject: values.subject,
      message: values.message,

      inquiry_type:
        inquiryType,

      project_id: null,

      consent_given:
        consent,

      source_page:
        window.location.pathname,

      website:
        website || null,
    }

    try {
      setIsSubmitting(true)

      const response =
        await publicContactService.createInquiry(
          payload
        )

      setSuccessMessage(
        response.message
      )

      form.reset()
    } catch (error) {
      if (isApiError(error)) {
        setSubmitError(
          error.isNetworkError
            ? "The server could not be reached. Please check your connection and try again."
            : error.message
        )
      } else {
        setSubmitError(
          "Your message could not be sent. Please try again."
        )
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="rounded-3xl border border-border/70 bg-card p-5 shadow-sm sm:p-8 lg:p-10">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">
          Send a message
        </p>

        <h2 className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl">
          Tell me what you&apos;re working on
        </h2>

        <p className="mt-3 leading-7 text-muted-foreground">
          Share a few details about the opportunity,
          collaboration, or project and I&apos;ll have
          the context needed to respond.
        </p>
      </div>

      {successMessage ? (
        <div
          className="mt-8 flex gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-4"
          role="status"
          aria-live="polite"
        >
          <CheckCircle2
            className="mt-0.5 size-5 shrink-0 text-primary"
            aria-hidden="true"
          />

          <div>
            <p className="font-medium">
              Message sent
            </p>

            <p className="mt-1 text-sm leading-6 text-muted-foreground">
              {successMessage}
            </p>
          </div>
        </div>
      ) : null}

      {submitError ? (
        <div
          className="mt-8 rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
          role="alert"
        >
          {submitError}
        </div>
      ) : null}

      <form
        className="mt-8"
        onSubmit={handleSubmit}
        noValidate
      >
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label
              htmlFor="contact-name"
              className="text-sm font-medium"
            >
              Name
              <span
                className="ml-1 text-destructive"
                aria-hidden="true"
              >
                *
              </span>
            </label>

            <input
              id="contact-name"
              name="name"
              type="text"
              autoComplete="name"
              maxLength={150}
              aria-invalid={
                Boolean(
                  fieldErrors.name
                )
              }
              aria-describedby={
                fieldErrors.name
                  ? "contact-name-error"
                  : undefined
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="Your name"
            />

            <div id="contact-name-error">
              <FieldError
                message={
                  fieldErrors.name
                }
              />
            </div>
          </div>

          <div>
            <label
              htmlFor="contact-email"
              className="text-sm font-medium"
            >
              Email
              <span
                className="ml-1 text-destructive"
                aria-hidden="true"
              >
                *
              </span>
            </label>

            <input
              id="contact-email"
              name="email"
              type="email"
              autoComplete="email"
              aria-invalid={
                Boolean(
                  fieldErrors.email
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="you@example.com"
            />

            <FieldError
              message={
                fieldErrors.email
              }
            />
          </div>

          <div>
            <label
              htmlFor="contact-phone"
              className="text-sm font-medium"
            >
              Phone
              <span className="ml-1 text-muted-foreground">
                optional
              </span>
            </label>

            <input
              id="contact-phone"
              name="phone"
              type="tel"
              autoComplete="tel"
              maxLength={40}
              aria-invalid={
                Boolean(
                  fieldErrors.phone
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="Phone number"
            />

            <FieldError
              message={
                fieldErrors.phone
              }
            />
          </div>

          <div>
            <label
              htmlFor="contact-company"
              className="text-sm font-medium"
            >
              Company
              <span className="ml-1 text-muted-foreground">
                optional
              </span>
            </label>

            <input
              id="contact-company"
              name="company"
              type="text"
              autoComplete="organization"
              maxLength={150}
              aria-invalid={
                Boolean(
                  fieldErrors.company
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              placeholder="Organization"
            />

            <FieldError
              message={
                fieldErrors.company
              }
            />
          </div>
        </div>

        <div className="mt-5">
          <label
            htmlFor="contact-inquiry-type"
            className="text-sm font-medium"
          >
            Inquiry type
          </label>

          <select
            id="contact-inquiry-type"
            name="inquiry_type"
            defaultValue="general"
            aria-invalid={
              Boolean(
                fieldErrors.inquiryType
              )
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
          >
            {inquiryTypeOptions.map(
              (option) => (
                <option
                  key={
                    option.value
                  }
                  value={
                    option.value
                  }
                >
                  {option.label}
                </option>
              )
            )}
          </select>

          <FieldError
            message={
              fieldErrors.inquiryType
            }
          />
        </div>

        <div className="mt-5">
          <label
            htmlFor="contact-subject"
            className="text-sm font-medium"
          >
            Subject
            <span
              className="ml-1 text-destructive"
              aria-hidden="true"
            >
              *
            </span>
          </label>

          <input
            id="contact-subject"
            name="subject"
            type="text"
            maxLength={200}
            aria-invalid={
              Boolean(
                fieldErrors.subject
              )
            }
            className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            placeholder="What would you like to discuss?"
          />

          <FieldError
            message={
              fieldErrors.subject
            }
          />
        </div>

        <div className="mt-5">
          <div className="flex items-end justify-between gap-4">
            <label
              htmlFor="contact-message"
              className="text-sm font-medium"
            >
              Message
              <span
                className="ml-1 text-destructive"
                aria-hidden="true"
              >
                *
              </span>
            </label>

            <span className="text-xs text-muted-foreground">
              Minimum 10 characters
            </span>
          </div>

          <textarea
            id="contact-message"
            name="message"
            rows={7}
            maxLength={10_000}
            aria-invalid={
              Boolean(
                fieldErrors.message
              )
            }
            className="mt-2 w-full resize-y rounded-lg border border-input bg-background px-3 py-3 text-sm leading-6 outline-none transition-shadow placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            placeholder="Tell me about the opportunity, project, or challenge..."
          />

          <FieldError
            message={
              fieldErrors.message
            }
          />
        </div>

        <div
          className="absolute -left-[10000px] top-auto size-px overflow-hidden"
          aria-hidden="true"
        >
          <label htmlFor="contact-website">
            Website
          </label>

          <input
            id="contact-website"
            name="website"
            type="text"
            tabIndex={-1}
            autoComplete="off"
          />
        </div>

        <div className="mt-6">
          <label className="flex cursor-pointer items-start gap-3">
            <input
              name="consent"
              type="checkbox"
              className="mt-1 size-4 shrink-0 rounded border-input"
              aria-invalid={
                Boolean(
                  fieldErrors.consent
                )
              }
            />

            <span className="text-sm leading-6 text-muted-foreground">
              I consent to the information in this
              form being used to review and respond
              to my inquiry.
            </span>
          </label>

          <FieldError
            message={
              fieldErrors.consent
            }
          />
        </div>

        <Button
          type="submit"
          size="lg"
          className="mt-8 w-full sm:w-auto"
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2
                className="animate-spin"
                aria-hidden="true"
              />

              Sending...
            </>
          ) : (
            <>
              Send message

              <Send
                aria-hidden="true"
              />
            </>
          )}
        </Button>
      </form>
    </div>
  )
}