"use client"

import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  AdminApiError,
  adminInquiryService,
} from "@/services/admin"

import type {
  AdminContactInquiryListResponse,
  ContactInquiryAdminRead,
  ContactInquiryAssigneeOption,
  ContactInquiryProjectOption,
  ContactInquiryStatistics,
  ContactInquiryStatus,
  ContactInquiryUpdate,
} from "@/types/contact"

import {
  AdminInquiryCard,
} from "./admin-inquiry-card"

import {
  AdminInquiryDetail,
  type InquiryBusyAction,
} from "./admin-inquiry-detail"

import {
  AdminInquiryFilters,
} from "./admin-inquiry-filters"

import {
  AdminInquiryStatistics,
} from "./admin-inquiry-statistics"

import {
  defaultInquiryAdminFilters,
  type InquiryAdminFilters,
} from "./inquiry-admin-filters"

const PAGE_SIZE = 10

const SEARCH_DEBOUNCE_MS =
  750

function errorMessage(
  error: unknown,
  fallback: string
): string {
  if (
    error instanceof
    AdminApiError
  ) {
    return error.message
  }

  if (
    error instanceof Error
  ) {
    return error.message
  }

  return fallback
}

function startOfDay(
  value: string
): string | undefined {
  return value
    ? `${value}T00:00:00.000Z`
    : undefined
}

function endOfDay(
  value: string
): string | undefined {
  return value
    ? `${value}T23:59:59.999Z`
    : undefined
}

export function AdminInquiryManager() {
  const [
    filters,
    setFilters,
  ] =
    useState<InquiryAdminFilters>(
      defaultInquiryAdminFilters
    )

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] =
    useState(
      filters.search
    )

  const [
    page,
    setPage,
  ] =
    useState(1)

  const [
    response,
    setResponse,
  ] =
    useState<AdminContactInquiryListResponse | null>(
      null
    )

  const [
    statistics,
    setStatistics,
  ] =
    useState<ContactInquiryStatistics | null>(
      null
    )

  const [
    assignees,
    setAssignees,
  ] =
    useState<
      ContactInquiryAssigneeOption[]
    >([])

  const [
    projects,
    setProjects,
  ] =
    useState<
      ContactInquiryProjectOption[]
    >([])

  const [
    selectedInquiryId,
    setSelectedInquiryId,
  ] =
    useState<string | null>(
      null
    )

  const [
    selectedInquiry,
    setSelectedInquiry,
  ] =
    useState<ContactInquiryAdminRead | null>(
      null
    )

  const [
    loadedListRequestKey,
    setLoadedListRequestKey,
  ] =
    useState<string | null>(
      null
    )

  const [
    loadedDetailRequestKey,
    setLoadedDetailRequestKey,
  ] =
    useState<string | null>(
      null
    )

  const [
    loadedStatisticsVersion,
    setLoadedStatisticsVersion,
  ] =
    useState<number | null>(
      null
    )

  const [
    busyAction,
    setBusyAction,
  ] =
    useState<InquiryBusyAction | null>(
      null
    )

  const [
    reloadVersion,
    setReloadVersion,
  ] =
    useState(0)

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null
    )

  const filterSearch =
    filters.search

  const filterInquiryType =
    filters.inquiryType

  const filterStatus =
    filters.status

  const filterPriority =
    filters.priority

  const filterReadState =
    filters.readState

  const filterAssignment =
    filters.assignment

  const filterProject =
    filters.project

  const filterCreatedFrom =
    filters.createdFrom

  const filterCreatedTo =
    filters.createdTo

  const filterIncludeDeleted =
    filters.includeDeleted

  const filterSortBy =
    filters.sortBy

  const filterSortDirection =
    filters.sortDirection

  const dateRangeError =
    filterCreatedFrom &&
    filterCreatedTo &&
    filterCreatedFrom >
      filterCreatedTo
      ? "The received-from date cannot be later than the received-to date."
      : null

  const listRequestKey =
    [
      page,
      debouncedSearch,
      filterInquiryType,
      filterStatus,
      filterPriority,
      filterReadState,
      filterAssignment,
      filterProject,
      filterCreatedFrom,
      filterCreatedTo,
      filterIncludeDeleted,
      filterSortBy,
      filterSortDirection,
      reloadVersion,
    ].join("|")

  const detailRequestKey =
    selectedInquiryId
      ? `${selectedInquiryId}:${reloadVersion}`
      : null

  const loadingList =
    !dateRangeError &&
    loadedListRequestKey !==
      listRequestKey

  const loadingDetail =
    detailRequestKey !==
      null &&
    loadedDetailRequestKey !==
      detailRequestKey

  const loadingStatistics =
    loadedStatisticsVersion !==
    reloadVersion

  const displayedError =
    dateRangeError ??
    error

  const assigneeNames =
    useMemo(
      () =>
        new Map(
          assignees.map(
            (
              assignee
            ) => [
              assignee.id,
              assignee.full_name,
            ]
          )
        ),
      [assignees]
    )

  const projectTitles =
    useMemo(
      () =>
        new Map(
          projects.map(
            (
              project
            ) => [
              project.id,
              project.title,
            ]
          )
        ),
      [projects]
    )

  useEffect(() => {
    let cancelled =
      false

    void Promise.all([
      adminInquiryService.getAssignees(),
      adminInquiryService.getProjects(),
    ])
      .then(
        ([
          assigneeResult,
          projectResult,
        ]) => {
          if (cancelled) {
            return
          }

          setAssignees(
            assigneeResult
          )

          setProjects(
            projectResult
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (cancelled) {
            return
          }

          setError(
            errorMessage(
              caughtError,
              "Inquiry lookup data could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [])

  useEffect(() => {
    let cancelled =
      false

    const requestVersion =
      reloadVersion

    void adminInquiryService
      .getStatistics()
      .then(
        (
          result
        ) => {
          if (cancelled) {
            return
          }

          setStatistics(
            result
          )

          setLoadedStatisticsVersion(
            requestVersion
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (cancelled) {
            return
          }

          setLoadedStatisticsVersion(
            requestVersion
          )

          setError(
            errorMessage(
              caughtError,
              "Inquiry statistics could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [reloadVersion])

  useEffect(() => {
    if (
      filterSearch ===
      debouncedSearch
    ) {
      return
    }

    const timeoutId =
      window.setTimeout(
        () => {
          setPage(1)

          setDebouncedSearch(
            filterSearch
          )
        },
        SEARCH_DEBOUNCE_MS
      )

    return () => {
      window.clearTimeout(
        timeoutId
      )
    }
  }, [
    filterSearch,
    debouncedSearch,
  ])

  useEffect(() => {
    if (dateRangeError) {
      return
    }

    let cancelled =
      false

    const currentRequestKey =
      listRequestKey

    let assignedToId:
      string | undefined

    let includeUnassigned =
      false

    if (
      filterAssignment ===
      "unassigned"
    ) {
      includeUnassigned =
        true
    } else if (
      filterAssignment !==
      "all"
    ) {
      assignedToId =
        filterAssignment
    }

    void adminInquiryService
      .getInquiries({
        page,

        page_size:
          PAGE_SIZE,

        search:
          debouncedSearch.trim() ||
          undefined,

        inquiry_type:
          filterInquiryType ===
          "all"
            ? undefined
            : filterInquiryType,

        inquiry_status:
          filterStatus ===
          "all"
            ? undefined
            : filterStatus,

        priority:
          filterPriority ===
          "all"
            ? undefined
            : filterPriority,

        is_read:
          filterReadState ===
          "all"
            ? undefined
            : filterReadState ===
                "read",

        assigned_to_id:
          assignedToId,

        include_unassigned:
          includeUnassigned,

        project_id:
          filterProject ===
          "all"
            ? undefined
            : filterProject,

        include_deleted:
          filterIncludeDeleted,

        created_from:
          startOfDay(
            filterCreatedFrom
          ),

        created_to:
          endOfDay(
            filterCreatedTo
          ),

        sort_by:
          filterSortBy,

        sort_direction:
          filterSortDirection,
      })
      .then(
        (
          result
        ) => {
          if (cancelled) {
            return
          }

          setResponse(
            result
          )

          setLoadedListRequestKey(
            currentRequestKey
          )

          setError(null)

          if (
            result.items.length ===
            0
          ) {
            setSelectedInquiry(
              null
            )
          }

          setSelectedInquiryId(
            (
              current
            ) => {
              if (
                current &&
                result.items.some(
                  (
                    inquiry
                  ) =>
                    inquiry.id ===
                    current
                )
              ) {
                return current
              }

              return (
                result.items[0]
                  ?.id ??
                null
              )
            }
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (cancelled) {
            return
          }

          setLoadedListRequestKey(
            currentRequestKey
          )

          setError(
            errorMessage(
              caughtError,
              "Inquiries could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    page,
    debouncedSearch,
    filterInquiryType,
    filterStatus,
    filterPriority,
    filterReadState,
    filterAssignment,
    filterProject,
    filterCreatedFrom,
    filterCreatedTo,
    filterIncludeDeleted,
    filterSortBy,
    filterSortDirection,
    reloadVersion,
    dateRangeError,
    listRequestKey,
  ])

  useEffect(() => {
    if (
      !selectedInquiryId ||
      !detailRequestKey
    ) {
      return
    }

    let cancelled =
      false

    const currentRequestKey =
      detailRequestKey

    void adminInquiryService
      .getInquiry(
        selectedInquiryId,
        {
          includeDeleted:
            true,
        }
      )
      .then(
        (
          result
        ) => {
          if (cancelled) {
            return
          }

          setSelectedInquiry(
            result
          )

          setLoadedDetailRequestKey(
            currentRequestKey
          )
        }
      )
      .catch(
        (
          caughtError:
            unknown
        ) => {
          if (cancelled) {
            return
          }

          setSelectedInquiry(
            null
          )

          setLoadedDetailRequestKey(
            currentRequestKey
          )

          setError(
            errorMessage(
              caughtError,
              "The selected inquiry could not be loaded."
            )
          )
        }
      )

    return () => {
      cancelled =
        true
    }
  }, [
    selectedInquiryId,
    detailRequestKey,
  ])

  function handleFiltersChange(
    nextFilters:
      InquiryAdminFilters
  ) {
    setError(null)

    setPage(1)

    setFilters(
      nextFilters
    )
  }

  async function runAction(
    action:
      InquiryBusyAction,

    operation:
      () =>
        Promise<ContactInquiryAdminRead>
  ) {
    if (busyAction) {
      return
    }

    setBusyAction(
      action
    )

    setError(null)

    try {
      const updated =
        await operation()

      setSelectedInquiry(
        updated
      )

      setReloadVersion(
        (
          current
        ) =>
          current + 1
      )
    } catch (
      caughtError
    ) {
      setError(
        errorMessage(
          caughtError,
          "The inquiry could not be updated."
        )
      )
    } finally {
      setBusyAction(
        null
      )
    }
  }

  async function handleSave(
    payload:
      ContactInquiryUpdate
  ) {
    if (
      !selectedInquiryId
    ) {
      return
    }

    await runAction(
      "update",
      () =>
        adminInquiryService.updateInquiry(
          selectedInquiryId,
          payload
        )
    )
  }

  async function handleReadState(
    isRead: boolean
  ) {
    if (
      !selectedInquiryId
    ) {
      return
    }

    await runAction(
      "read-state",
      () =>
        adminInquiryService.updateReadState(
          selectedInquiryId,
          {
            is_read:
              isRead,
          }
        )
    )
  }

  async function handleStatus(
    status:
      ContactInquiryStatus
  ) {
    if (
      !selectedInquiryId
    ) {
      return
    }

    await runAction(
      "status",
      () =>
        adminInquiryService.updateStatus(
          selectedInquiryId,
          {
            status,
          }
        )
    )
  }

  async function handleDelete() {
    if (
      !selectedInquiryId
    ) {
      return
    }

    const confirmed =
      window.confirm(
        "Delete this inquiry? It can be restored later."
      )

    if (!confirmed) {
      return
    }

    await runAction(
      "delete",
      () =>
        adminInquiryService.deleteInquiry(
          selectedInquiryId,
          {
            reason:
              "Deleted from the administrative inquiry inbox.",
          }
        )
    )

    setFilters(
      (
        current
      ) => ({
        ...current,

        includeDeleted:
          true,
      })
    )

    setPage(1)
  }

  async function handleRestore() {
    if (
      !selectedInquiryId
    ) {
      return
    }

    await runAction(
      "restore",
      () =>
        adminInquiryService.restoreInquiry(
          selectedInquiryId,
          {
            status:
              "new",

            priority:
              "normal",

            reason:
              "Restored for renewed administrative review.",
          }
        )
    )
  }

  const items =
    response?.items ??
    []

  const totalPages =
    response?.total_pages ??
    0

  const selectedInquiryIsCurrent =
    selectedInquiry !==
      null &&
    selectedInquiry.id ===
      selectedInquiryId

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-primary">
          Contact CRM
        </p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight">
          Inquiries
        </h1>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Review incoming
          messages, prioritize
          opportunities, assign
          follow-up work and move
          each inquiry through its
          administrative
          lifecycle.
        </p>
      </div>

      <AdminInquiryStatistics
        statistics={
          statistics
        }
        loading={
          loadingStatistics
        }
      />

      <AdminInquiryFilters
        filters={filters}
        assignees={
          assignees
        }
        projects={
          projects
        }
        disabled={
          Boolean(
            busyAction
          )
        }
        onChange={
          handleFiltersChange
        }
      />

      {displayedError ? (
        <div
          role="alert"
          className="rounded-xl border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive"
        >
          {displayedError}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
        <section className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="font-semibold">
                Inbox
              </h2>

              <p className="text-sm text-muted-foreground">
                {response
                  ? `${response.total_items} inquiry${response.total_items === 1 ? "" : "ies"}`
                  : "Loading inquiries..."}
              </p>
            </div>

            {loadingList ? (
              <span className="text-xs text-muted-foreground">
                Refreshing...
              </span>
            ) : null}
          </div>

          {items.length >
          0 ? (
            <div className="space-y-3">
              {items.map(
                (
                  inquiry
                ) => (
                  <AdminInquiryCard
                    key={
                      inquiry.id
                    }
                    inquiry={
                      inquiry
                    }
                    selected={
                      inquiry.id ===
                      selectedInquiryId
                    }
                    disabled={
                      Boolean(
                        busyAction
                      )
                    }
                    assigneeName={
                      inquiry.assigned_to_id
                        ? assigneeNames.get(
                            inquiry.assigned_to_id
                          )
                        : undefined
                    }
                    projectTitle={
                      inquiry.project_id
                        ? projectTitles.get(
                            inquiry.project_id
                          )
                        : undefined
                    }
                    onSelect={() => {
                      setError(null)

                      setSelectedInquiryId(
                        inquiry.id
                      )
                    }}
                  />
                )
              )}
            </div>
          ) : loadingList ? (
            <div className="rounded-2xl border border-dashed border-border p-8 text-center text-sm text-muted-foreground">
              Loading
              inquiries...
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-8 text-center">
              <p className="font-medium">
                No inquiries found
              </p>

              <p className="mt-2 text-sm text-muted-foreground">
                Try changing the
                search or filter
                settings.
              </p>
            </div>
          )}

          {response &&
          totalPages > 0 ? (
            <div className="flex items-center justify-between gap-3 rounded-xl border border-border/70 bg-card p-3">
              <button
                type="button"
                disabled={
                  !response.has_previous_page ||
                  loadingList
                }
                onClick={() => {
                  setError(null)

                  setPage(
                    (
                      current
                    ) =>
                      Math.max(
                        1,
                        current -
                          1
                      )
                  )
                }}
                className="inline-flex h-9 items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium hover:bg-muted disabled:pointer-events-none disabled:opacity-50"
              >
                Previous
              </button>

              <span className="text-xs text-muted-foreground">
                Page{" "}
                {
                  response.page
                }{" "}
                of{" "}
                {
                  response.total_pages
                }
              </span>

              <button
                type="button"
                disabled={
                  !response.has_next_page ||
                  loadingList
                }
                onClick={() => {
                  setError(null)

                  setPage(
                    (
                      current
                    ) =>
                      current +
                      1
                  )
                }}
                className="inline-flex h-9 items-center justify-center rounded-lg border border-input bg-background px-3 text-sm font-medium hover:bg-muted disabled:pointer-events-none disabled:opacity-50"
              >
                Next
              </button>
            </div>
          ) : null}
        </section>

        <div>
          {loadingDetail ? (
            <div className="rounded-2xl border border-border/70 bg-card p-10 text-center text-sm text-muted-foreground">
              Loading inquiry
              details...
            </div>
          ) : selectedInquiryIsCurrent &&
            selectedInquiry ? (
            <AdminInquiryDetail
              key={`${selectedInquiry.id}:${selectedInquiry.updated_at}:${selectedInquiry.deleted_at ?? ""}`}
              inquiry={
                selectedInquiry
              }
              assignees={
                assignees
              }
              projects={
                projects
              }
              busyAction={
                busyAction
              }
              onSave={
                handleSave
              }
              onReadState={
                handleReadState
              }
              onStatus={
                handleStatus
              }
              onDelete={
                handleDelete
              }
              onRestore={
                handleRestore
              }
            />
          ) : (
            <div className="rounded-2xl border border-dashed border-border p-10 text-center">
              <p className="font-medium">
                Select an inquiry
              </p>

              <p className="mt-2 text-sm text-muted-foreground">
                Choose a message
                from the inbox to
                review its full
                details and
                workflow.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}