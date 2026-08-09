import type {
  EmploymentType,
  ExperienceLocationType,
  AdminExperienceSortDirection,
  AdminExperienceSortField,
} from "@/types/portfolio/experience"

export type ExperienceBooleanFilter =
  | "all"
  | "yes"
  | "no"

export type ExperienceEmploymentFilter =
  | "all"
  | EmploymentType

export type ExperienceLocationFilter =
  | "all"
  | ExperienceLocationType

export type ExperienceAdminFilterState = {
  search: string

  employmentType:
    ExperienceEmploymentFilter

  locationType:
    ExperienceLocationFilter

  current:
    ExperienceBooleanFilter

  visibility:
    ExperienceBooleanFilter

  featured:
    ExperienceBooleanFilter

  includeDeleted:
    boolean

  sortBy:
    AdminExperienceSortField

  sortDirection:
    AdminExperienceSortDirection
}

export const defaultExperienceAdminFilters:
  ExperienceAdminFilterState = {
    search:
      "",

    employmentType:
      "all",

    locationType:
      "all",

    current:
      "all",

    visibility:
      "all",

    featured:
      "all",

    includeDeleted:
      false,

    sortBy:
      "start_date",

    sortDirection:
      "desc",
  }