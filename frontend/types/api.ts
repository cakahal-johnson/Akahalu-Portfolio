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

export type ApiErrorBody = {
  detail?: string
  message?: string
  code?: string
  errors?: ApiFieldError[]
}

export type ApiPagination = {
  page: number
  page_size: number
  total: number
  total_pages: number
}

export type PaginatedApiResponse<T> = {
  items: T[]
  page: number
  page_size: number
  total: number
  total_pages: number
}

export type ApiListResponse<T> =
  | T[]
  | {
      items: T[]
    }

export type ApiRequestParams = Record<
  string,
  ApiPrimitive | ApiPrimitive[] | undefined
>

export type ApiSuccessResponse<T> = {
  data: T
}

export type EmptyApiResponse = undefined