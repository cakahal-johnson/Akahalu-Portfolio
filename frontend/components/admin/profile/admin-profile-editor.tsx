"use client"

import {
  CheckCircle2,
  Eye,
  EyeOff,
  Loader2,
  Save,
} from "lucide-react"
import {
  useEffect,
  useState,
  type FormEvent,
} from "react"

import { Button } from "@/components/ui/button"
import {
  AdminApiError,
  adminProfileService,
} from "@/services/admin"

import type {
  ProfileAdminRead,
  ProfileAdminUpdate,
  ProfileAvailabilityStatus,
} from "@/types/portfolio/profile"

type ProfileFormState = {
  first_name: string
  middle_name: string
  last_name: string

  display_name: string

  professional_title: string
  headline: string

  short_bio: string
  biography: string

  location: string
  country: string
  timezone: string

  primary_email: string
  phone: string

  website_url: string
  resume_url: string
  profile_image_url: string

  years_of_experience: string

  availability_status: ProfileAvailabilityStatus
  availability_message: string

  seo_title: string
  seo_description: string
}

const emptyForm: ProfileFormState = {
  first_name: "",
  middle_name: "",
  last_name: "",

  display_name: "",

  professional_title: "",
  headline: "",

  short_bio: "",
  biography: "",

  location: "",
  country: "",
  timezone: "",

  primary_email: "",
  phone: "",

  website_url: "",
  resume_url: "",
  profile_image_url: "",

  years_of_experience: "0",

  availability_status:
    "open_to_opportunities",

  availability_message: "",

  seo_title: "",
  seo_description: "",
}

function profileToForm(
  profile: ProfileAdminRead
): ProfileFormState {
  return {
    first_name:
      profile.first_name,

    middle_name:
      profile.middle_name ??
      "",

    last_name:
      profile.last_name,

    display_name:
      profile.display_name,

    professional_title:
      profile.professional_title,

    headline:
      profile.headline,

    short_bio:
      profile.short_bio,

    biography:
      profile.biography,

    location:
      profile.location ??
      "",

    country:
      profile.country ??
      "",

    timezone:
      profile.timezone ??
      "",

    primary_email:
      profile.primary_email,

    phone:
      profile.phone ??
      "",

    website_url:
      profile.website_url ??
      "",

    resume_url:
      profile.resume_url ??
      "",

    profile_image_url:
      profile.profile_image_url ??
      "",

    years_of_experience:
      String(
        profile.years_of_experience
      ),

    availability_status:
      profile.availability_status,

    availability_message:
      profile.availability_message ??
      "",

    seo_title:
      profile.seo_title ??
      "",

    seo_description:
      profile.seo_description ??
      "",
  }
}

function nullable(
  value: string
): string | null {
  const normalized =
    value.trim()

  return normalized
    ? normalized
    : null
}

function formToPayload(
  form: ProfileFormState
): ProfileAdminUpdate {
  return {
    first_name:
      form.first_name.trim(),

    middle_name:
      nullable(
        form.middle_name
      ),

    last_name:
      form.last_name.trim(),

    display_name:
      form.display_name.trim(),

    professional_title:
      form.professional_title.trim(),

    headline:
      form.headline.trim(),

    short_bio:
      form.short_bio.trim(),

    biography:
      form.biography.trim(),

    location:
      nullable(
        form.location
      ),

    country:
      nullable(
        form.country
      ),

    timezone:
      nullable(
        form.timezone
      ),

    primary_email:
      form.primary_email
        .trim()
        .toLowerCase(),

    phone:
      nullable(
        form.phone
      ),

    website_url:
      nullable(
        form.website_url
      ),

    resume_url:
      nullable(
        form.resume_url
      ),

    profile_image_url:
      nullable(
        form.profile_image_url
      ),

    years_of_experience:
      Number(
        form.years_of_experience
      ),

    availability_status:
      form.availability_status,

    availability_message:
      nullable(
        form.availability_message
      ),

    seo_title:
      nullable(
        form.seo_title
      ),

    seo_description:
      nullable(
        form.seo_description
      ),
  }
}

type TextFieldProps = {
  label: string
  value: string
  onChange: (
    value: string
  ) => void
  type?: string
  required?: boolean
  minLength?: number
  maxLength?: number
  placeholder?: string
}

function TextField({
  label,
  value,
  onChange,
  type = "text",
  required = false,
  minLength,
  maxLength,
  placeholder,
}: TextFieldProps) {
  return (
    <label className="block">
      <span className="text-sm font-medium">
        {label}
      </span>

      <input
        type={type}
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value
          )
        }
        required={required}
        minLength={minLength}
        maxLength={maxLength}
        placeholder={placeholder}
        className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none transition-shadow focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
      />
    </label>
  )
}

export function AdminProfileEditor() {
  const [
    profile,
    setProfile,
  ] =
    useState<ProfileAdminRead | null>(
      null
    )

  const [
    form,
    setForm,
  ] =
    useState<ProfileFormState>(
      emptyForm
    )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    saving,
    setSaving,
  ] = useState(false)

  const [
    visibilitySaving,
    setVisibilitySaving,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  )

  const [
    success,
    setSuccess,
  ] = useState<string | null>(
    null
  )

  useEffect(() => {
    let cancelled = false

    async function loadProfile() {
      try {
        const result =
          await adminProfileService.getProfile()

        if (!cancelled) {
          setProfile(result)

          setForm(
            profileToForm(
              result
            )
          )
        }
      } catch (caughtError) {
        if (cancelled) {
          return
        }

        setError(
          caughtError instanceof
          AdminApiError
            ? caughtError.message
            : "The portfolio profile could not be loaded."
        )
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadProfile()

    return () => {
      cancelled = true
    }
  }, [])

  function updateField<
    TKey extends keyof ProfileFormState,
  >(
    key: TKey,
    value: ProfileFormState[TKey]
  ) {
    setForm(
      (current) => ({
        ...current,
        [key]: value,
      })
    )

    setSuccess(null)
  }

  async function saveProfile(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault()

    if (saving) {
      return
    }

    const years =
      Number(
        form.years_of_experience
      )

    if (
      !Number.isInteger(years) ||
      years < 0 ||
      years > 100
    ) {
      setError(
        "Years of experience must be a whole number between 0 and 100."
      )

      return
    }

    try {
      setSaving(true)
      setError(null)
      setSuccess(null)

      const updated =
        await adminProfileService.updateProfile(
          formToPayload(form)
        )

      setProfile(updated)

      setForm(
        profileToForm(
          updated
        )
      )

      setSuccess(
        "Portfolio profile saved successfully."
      )
    } catch (caughtError) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "The portfolio profile could not be saved."
      )
    } finally {
      setSaving(false)
    }
  }

  async function toggleVisibility() {
    if (
      !profile ||
      visibilitySaving
    ) {
      return
    }

    try {
      setVisibilitySaving(true)
      setError(null)
      setSuccess(null)

      const nextValue =
        !profile.is_public

      const updated =
        await adminProfileService.updateVisibility(
          {
            is_public:
              nextValue,

            reason:
              nextValue
                ? "Published from portfolio administration."
                : "Hidden from portfolio administration.",
          }
        )

      setProfile(updated)

      setSuccess(
        nextValue
          ? "Portfolio profile is now public."
          : "Portfolio profile is now private."
      )
    } catch (caughtError) {
      setError(
        caughtError instanceof
        AdminApiError
          ? caughtError.message
          : "Profile visibility could not be updated."
      )
    } finally {
      setVisibilitySaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-72 items-center justify-center rounded-2xl border border-border bg-background">
        <div className="flex items-center gap-3 text-sm text-muted-foreground">
          <Loader2
            className="size-5 animate-spin"
            aria-hidden="true"
          />

          Loading portfolio profile...
        </div>
      </div>
    )
  }

  if (
    error &&
    !profile
  ) {
    return (
      <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-6">
        <p className="font-medium text-destructive">
          Profile unavailable
        </p>

        <p className="mt-2 text-sm text-destructive/90">
          {error}
        </p>
      </div>
    )
  }

  if (!profile) {
    return null
  }

  return (
    <form
      onSubmit={saveProfile}
      className="space-y-6"
    >
      {error ? (
        <div
          className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
          role="alert"
        >
          {error}
        </div>
      ) : null}

      {success ? (
        <div
          className="flex items-start gap-3 rounded-xl border border-primary/20 bg-primary/5 p-4 text-sm"
          role="status"
        >
          <CheckCircle2
            className="mt-0.5 size-4 shrink-0 text-primary"
            aria-hidden="true"
          />

          {success}
        </div>
      ) : null}

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold">
              Public visibility
            </h2>

            <p className="mt-1 text-sm text-muted-foreground">
              Control whether the profile is available through the public portfolio API.
            </p>
          </div>

          <Button
            type="button"
            variant={
              profile.is_public
                ? "outline"
                : "default"
            }
            onClick={
              toggleVisibility
            }
            disabled={
              visibilitySaving
            }
          >
            {visibilitySaving ? (
              <Loader2
                className="animate-spin"
                aria-hidden="true"
              />
            ) : profile.is_public ? (
              <EyeOff
                aria-hidden="true"
              />
            ) : (
              <Eye
                aria-hidden="true"
              />
            )}

            {profile.is_public
              ? "Make private"
              : "Publish profile"}
          </Button>
        </div>

        <div className="mt-4 flex items-center gap-2 text-sm">
          <span
            className={
              profile.is_public
                ? "size-2.5 rounded-full bg-emerald-500"
                : "size-2.5 rounded-full bg-muted-foreground"
            }
          />

          {profile.is_public
            ? "Currently public"
            : "Currently private"}
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Identity
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <TextField
            label="First name"
            value={
              form.first_name
            }
            onChange={(value) =>
              updateField(
                "first_name",
                value
              )
            }
            required
            minLength={2}
            maxLength={100}
          />

          <TextField
            label="Middle name"
            value={
              form.middle_name
            }
            onChange={(value) =>
              updateField(
                "middle_name",
                value
              )
            }
            maxLength={100}
          />

          <TextField
            label="Last name"
            value={
              form.last_name
            }
            onChange={(value) =>
              updateField(
                "last_name",
                value
              )
            }
            required
            minLength={2}
            maxLength={100}
          />

          <TextField
            label="Display name"
            value={
              form.display_name
            }
            onChange={(value) =>
              updateField(
                "display_name",
                value
              )
            }
            required
            minLength={2}
            maxLength={200}
          />

          <TextField
            label="Professional title"
            value={
              form.professional_title
            }
            onChange={(value) =>
              updateField(
                "professional_title",
                value
              )
            }
            required
            minLength={2}
            maxLength={200}
          />

          <TextField
            label="Years of experience"
            type="number"
            value={
              form.years_of_experience
            }
            onChange={(value) =>
              updateField(
                "years_of_experience",
                value
              )
            }
          />
        </div>

        <div className="mt-5">
          <label className="block">
            <span className="text-sm font-medium">
              Headline
            </span>

            <input
              value={
                form.headline
              }
              onChange={(event) =>
                updateField(
                  "headline",
                  event.target.value
                )
              }
              required
              minLength={5}
              maxLength={300}
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Biography
        </h2>

        <div className="mt-5">
          <label className="block">
            <span className="text-sm font-medium">
              Short bio
            </span>

            <textarea
              value={
                form.short_bio
              }
              onChange={(event) =>
                updateField(
                  "short_bio",
                  event.target.value
                )
              }
              required
              minLength={20}
              maxLength={500}
              rows={4}
              className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />

            <p className="mt-1 text-xs text-muted-foreground">
              {form.short_bio.length}/500
            </p>
          </label>
        </div>

        <div className="mt-5">
          <label className="block">
            <span className="text-sm font-medium">
              Full biography
            </span>

            <textarea
              value={
                form.biography
              }
              onChange={(event) =>
                updateField(
                  "biography",
                  event.target.value
                )
              }
              required
              minLength={50}
              maxLength={10000}
              rows={10}
              className="mt-2 w-full resize-y rounded-lg border border-input bg-background p-3 text-sm leading-6 outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Contact & location
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="Public email"
            type="email"
            value={
              form.primary_email
            }
            onChange={(value) =>
              updateField(
                "primary_email",
                value
              )
            }
            required
          />

          <TextField
            label="Phone"
            value={
              form.phone
            }
            onChange={(value) =>
              updateField(
                "phone",
                value
              )
            }
            maxLength={40}
          />

          <TextField
            label="Location"
            value={
              form.location
            }
            onChange={(value) =>
              updateField(
                "location",
                value
              )
            }
            maxLength={200}
          />

          <TextField
            label="Country"
            value={
              form.country
            }
            onChange={(value) =>
              updateField(
                "country",
                value
              )
            }
            maxLength={100}
          />

          <TextField
            label="Timezone"
            value={
              form.timezone
            }
            onChange={(value) =>
              updateField(
                "timezone",
                value
              )
            }
            maxLength={100}
            placeholder="America/Regina"
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Links & media
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="Website URL"
            type="url"
            value={
              form.website_url
            }
            onChange={(value) =>
              updateField(
                "website_url",
                value
              )
            }
          />

          <TextField
            label="Résumé URL"
            type="url"
            value={
              form.resume_url
            }
            onChange={(value) =>
              updateField(
                "resume_url",
                value
              )
            }
          />

          <div className="md:col-span-2">
            <TextField
              label="Profile image URL"
              type="url"
              value={
                form.profile_image_url
              }
              onChange={(value) =>
                updateField(
                  "profile_image_url",
                  value
                )
              }
            />
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Availability
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium">
              Status
            </span>

            <select
              value={
                form.availability_status
              }
              onChange={(event) =>
                updateField(
                  "availability_status",
                  event.target.value as ProfileAvailabilityStatus
                )
              }
              className="mt-2 h-11 w-full rounded-lg border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="available">
                Available
              </option>

              <option value="open_to_opportunities">
                Open to opportunities
              </option>

              <option value="limited_availability">
                Limited availability
              </option>

              <option value="unavailable">
                Unavailable
              </option>
            </select>
          </label>

          <TextField
            label="Availability message"
            value={
              form.availability_message
            }
            onChange={(value) =>
              updateField(
                "availability_message",
                value
              )
            }
            maxLength={300}
          />
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-background p-5 sm:p-6">
        <h2 className="text-lg font-semibold">
          Search metadata
        </h2>

        <div className="mt-5 grid gap-5 md:grid-cols-2">
          <TextField
            label="SEO title"
            value={
              form.seo_title
            }
            onChange={(value) =>
              updateField(
                "seo_title",
                value
              )
            }
            maxLength={70}
          />

          <TextField
            label="SEO description"
            value={
              form.seo_description
            }
            onChange={(value) =>
              updateField(
                "seo_description",
                value
              )
            }
            maxLength={170}
          />
        </div>
      </section>

      <div className="sticky bottom-4 z-20 flex justify-end">
        <div className="rounded-xl border border-border bg-background/95 p-2 shadow-lg backdrop-blur">
          <Button
            type="submit"
            size="lg"
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2
                  className="animate-spin"
                  aria-hidden="true"
                />

                Saving...
              </>
            ) : (
              <>
                <Save
                  aria-hidden="true"
                />

                Save profile
              </>
            )}
          </Button>
        </div>
      </div>
    </form>
  )
}