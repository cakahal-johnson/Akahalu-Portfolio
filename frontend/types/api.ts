export type ApiPrimitive =
  | string
  | number
  | boolean
  | null

export type ApiFieldError = {
  field?: string
  message: string
  code?: string
}

export type ApiErrorDetail = {
  code?: string
  message?: string
}

export type ApiErrorBody = {
  detail?: string | ApiErrorDetail
  message?: string
  code?: string
  errors?: ApiFieldError[]
}

export type PaginatedApiResponse<T> = {
  items: T[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
  has_next_page: boolean
  has_previous_page: boolean
}

export type ApiRequestParams = Record<
  string,
  ApiPrimitive | ApiPrimitive[] | undefined
>

export type ApiSuccessResponse<T> = {
  data: T
}

export type EmptyApiResponse = undefined