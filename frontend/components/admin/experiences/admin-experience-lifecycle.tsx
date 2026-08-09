"use client"

import {
  Eye,
  EyeOff,
  Loader2,
  RotateCcw,
  Star,
  StarOff,
  Trash2,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import type {
  ExperienceAdminRead,
} from "@/types/portfolio/experience"

export type ExperienceBusyAction =
  | "visibility"
  | "featured"
  | "delete"
  | "restore"

type AdminExperienceLifecycleProps = {
  experience:
    ExperienceAdminRead

  busyAction:
    ExperienceBusyAction | null

  onToggleVisibility: (
    experience:
      ExperienceAdminRead
  ) => void

  onToggleFeatured: (
    experience:
      ExperienceAdminRead
  ) => void

  onDelete: (
    experience:
      ExperienceAdminRead
  ) => void

  onRestore: (
    experience:
      ExperienceAdminRead
  ) => void
}

export function AdminExperienceLifecycle({
  experience,
  busyAction,
  onToggleVisibility,
  onToggleFeatured,
  onDelete,
  onRestore,
}: AdminExperienceLifecycleProps) {
  const deleted =
    experience.deleted_at !==
    null

  const busy =
    busyAction !==
    null

  if (
    deleted
  ) {
    return (
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={
          busy
        }
        onClick={() =>
          onRestore(
            experience
          )
        }
      >
        {busyAction ===
        "restore" ? (
          <Loader2
            className="animate-spin"
            aria-hidden="true"
          />
        ) : (
          <RotateCcw
            aria-hidden="true"
          />
        )}

        Restore
      </Button>
    )
  }

  return (
    <>
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={
          busy
        }
        onClick={() =>
          onToggleVisibility(
            experience
          )
        }
      >
        {busyAction ===
        "visibility" ? (
          <Loader2
            className="animate-spin"
            aria-hidden="true"
          />
        ) : experience.is_public ? (
          <EyeOff
            aria-hidden="true"
          />
        ) : (
          <Eye
            aria-hidden="true"
          />
        )}

        {experience.is_public
          ? "Make private"
          : "Make public"}
      </Button>

      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={
          busy ||
          !experience.is_public
        }
        title={
          experience.is_public
            ? undefined
            : "Make this experience public before featuring it."
        }
        onClick={() =>
          onToggleFeatured(
            experience
          )
        }
      >
        {busyAction ===
        "featured" ? (
          <Loader2
            className="animate-spin"
            aria-hidden="true"
          />
        ) : experience.is_featured ? (
          <StarOff
            aria-hidden="true"
          />
        ) : (
          <Star
            aria-hidden="true"
          />
        )}

        {experience.is_featured
          ? "Unfeature"
          : "Feature"}
      </Button>

      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={
          busy
        }
        onClick={() =>
          onDelete(
            experience
          )
        }
      >
        {busyAction ===
        "delete" ? (
          <Loader2
            className="animate-spin"
            aria-hidden="true"
          />
        ) : (
          <Trash2
            aria-hidden="true"
          />
        )}

        Delete
      </Button>
    </>
  )
}