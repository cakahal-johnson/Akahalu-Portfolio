export type ContactInquiryType =
  | "general"
  | "employment"
  | "freelance"
  | "contract"
  | "collaboration"
  | "project"
  | "support"
  | "other"

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