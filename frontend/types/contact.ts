import type {
  PaginatedApiResponse,
} from "@/types/api"

export type ContactInquiryType =
  | "general"
  | "employment"
  | "freelance"
  | "contract"
  | "collaboration"
  | "project"
  | "support"
  | "other"

export type ContactInquiryStatus =
  | "new"
  | "in_progress"
  | "responded"
  | "closed"
  | "spam"

export type ContactInquiryPriority =
  | "low"
  | "normal"
  | "high"
  | "urgent"

export type ContactInquiryRestoreStatus =
  | "new"
  | "in_progress"
  | "spam"

export type ContactInquiryPublicCreate = {
  name: string
  email: string

  phone?: string | null
  company?: string | null

  subject: string
  message: string

  inquiry_type?: ContactInquiryType

  project_id?: string | null

  consent_given?: boolean

  source_page?: string | null

  /**
   * Honeypot field.
   * Legitimate clients must leave this empty.
   */
  website?: string | null
}

export type ContactInquiryPublicResponse = {
  message: string
}

export type ContactInquiryAssigneeOption = {
  id: string

  full_name: string
  email: string
}

export type ContactInquiryProjectOption = {
  id: string

  title: string
  slug: string
}

export type ContactInquirySummary = {
  id: string

  name: string
  email: string

  subject: string

  inquiry_type:
    ContactInquiryType

  status:
    ContactInquiryStatus

  priority:
    ContactInquiryPriority

  is_read: boolean

  assigned_to_id:
    string | null

  project_id:
    string | null

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ContactInquiryAdminRead = {
  id: string

  name: string
  email: string

  phone: string | null
  company: string | null

  subject: string
  message: string

  inquiry_type:
    ContactInquiryType

  status:
    ContactInquiryStatus

  priority:
    ContactInquiryPriority

  is_read: boolean

  read_at:
    string | null

  responded_at:
    string | null

  closed_at:
    string | null

  assigned_to_id:
    string | null

  project_id:
    string | null

  internal_notes:
    string | null

  consent_given: boolean

  source_page:
    string | null

  user_agent:
    string | null

  ip_address_hash:
    string | null

  submission_fingerprint:
    string | null

  created_at: string
  updated_at: string
  deleted_at: string | null
}

export type ContactInquiryUpdate = {
  priority?:
    ContactInquiryPriority | null

  assigned_to_id?:
    string | null

  internal_notes?:
    string | null

  inquiry_type?:
    ContactInquiryType | null
}

export type ContactInquiryReadUpdate = {
  is_read: boolean
}

export type ContactInquiryStatusUpdate = {
  status:
    ContactInquiryStatus

  reason?:
    string | null
}

export type ContactInquiryDeleteRequest = {
  reason?:
    string | null
}

export type ContactInquiryRestoreRequest = {
  status?:
    ContactInquiryRestoreStatus

  priority?:
    ContactInquiryPriority

  reason?:
    string | null
}

export type ContactInquiryStatistics = {
  new: number

  in_progress: number

  responded: number

  closed: number

  spam: number

  unread: number

  requires_attention: number
}

export type AdminContactInquirySortField =
  | "name"
  | "email"
  | "subject"
  | "inquiry_type"
  | "status"
  | "priority"
  | "is_read"
  | "created_at"
  | "updated_at"

export type AdminContactInquirySortDirection =
  | "asc"
  | "desc"

export type AdminContactInquiryListParams = {
  page?: number
  page_size?: number

  search?: string

  inquiry_type?:
    ContactInquiryType

  inquiry_status?:
    ContactInquiryStatus

  priority?:
    ContactInquiryPriority

  is_read?: boolean

  assigned_to_id?:
    string

  project_id?:
    string

  include_unassigned?:
    boolean

  include_deleted?:
    boolean

  created_from?:
    string

  created_to?:
    string

  sort_by?:
    AdminContactInquirySortField

  sort_direction?:
    AdminContactInquirySortDirection
}

export type AdminContactInquiryListResponse =
  PaginatedApiResponse<ContactInquirySummary>