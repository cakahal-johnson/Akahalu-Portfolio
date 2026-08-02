import {
  apiEndpoints,
  apiPost,
} from "@/lib/api"

import type {
  ContactInquiryPublicCreate,
  ContactInquiryPublicResponse,
} from "@/types/contact"

export const publicContactService = {
  createInquiry(
    payload: ContactInquiryPublicCreate,
    signal?: AbortSignal
  ): Promise<ContactInquiryPublicResponse> {
    return apiPost<
      ContactInquiryPublicResponse,
      ContactInquiryPublicCreate
    >(
      apiEndpoints.contact.inquiries,
      payload,
      {
        signal,
      }
    )
  },
} as const