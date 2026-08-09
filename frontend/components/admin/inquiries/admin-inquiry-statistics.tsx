import type {
  ContactInquiryStatistics,
} from "@/types/contact"

type AdminInquiryStatisticsProps = {
  statistics:
    ContactInquiryStatistics | null

  loading?: boolean
}

type StatisticItem = {
  key:
    keyof ContactInquiryStatistics

  label: string

  description: string
}

const statisticItems: StatisticItem[] =
  [
    {
      key: "new",
      label: "New",
      description:
        "New inquiries awaiting review",
    },
    {
      key: "in_progress",
      label: "In progress",
      description:
        "Currently being handled",
    },
    {
      key: "responded",
      label: "Responded",
      description:
        "Marked as responded",
    },
    {
      key: "closed",
      label: "Closed",
      description:
        "Completed inquiries",
    },
    {
      key: "spam",
      label: "Spam",
      description:
        "Messages classified as spam",
    },
    {
      key: "unread",
      label: "Unread",
      description:
        "Messages not yet reviewed",
    },
    {
      key: "requires_attention",
      label: "Attention",
      description:
        "High or urgent active inquiries",
    },
  ]

export function AdminInquiryStatistics({
  statistics,
  loading = false,
}: AdminInquiryStatisticsProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {statisticItems.map(
        (item) => {
          const value =
            statistics?.[
              item.key
            ]

          return (
            <div
              key={
                item.key
              }
              className="rounded-2xl border border-border/70 bg-card p-4 shadow-sm"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                {item.label}
              </p>

              <p className="mt-2 text-2xl font-bold tracking-tight">
                {loading
                  ? "—"
                  : (value ??
                    0)}
              </p>

              <p className="mt-1 text-xs leading-5 text-muted-foreground">
                {
                  item.description
                }
              </p>
            </div>
          )
        }
      )}
    </div>
  )
}