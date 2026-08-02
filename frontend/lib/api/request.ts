import type {
  AxiosRequestConfig,
  Method,
} from "axios"

import { apiClient } from "@/lib/api/client"
import { normalizeApiError } from "@/lib/api/errors"

type ApiRequestOptions<TBody = unknown> = {
  method?: Method
  params?: AxiosRequestConfig["params"]
  body?: TBody
  headers?: AxiosRequestConfig["headers"]
  signal?: AbortSignal
}

export async function apiRequest<
  TResponse,
  TBody = unknown,
>(
  url: string,
  options: ApiRequestOptions<TBody> = {}
): Promise<TResponse> {
  try {
    const response = await apiClient.request<TResponse>({
      url,
      method: options.method ?? "GET",
      params: options.params,
      data: options.body,
      headers: options.headers,
      signal: options.signal,
    })

    return response.data
  } catch (error) {
    throw normalizeApiError(error)
  }
}

export function apiGet<TResponse>(
  url: string,
  options: Omit<
    ApiRequestOptions<never>,
    "method" | "body"
  > = {}
): Promise<TResponse> {
  return apiRequest<TResponse>(url, {
    ...options,
    method: "GET",
  })
}

export function apiPost<TResponse, TBody>(
  url: string,
  body: TBody,
  options: Omit<
    ApiRequestOptions<TBody>,
    "method" | "body"
  > = {}
): Promise<TResponse> {
  return apiRequest<TResponse, TBody>(url, {
    ...options,
    method: "POST",
    body,
  })
}

export function apiPatch<TResponse, TBody>(
  url: string,
  body: TBody,
  options: Omit<
    ApiRequestOptions<TBody>,
    "method" | "body"
  > = {}
): Promise<TResponse> {
  return apiRequest<TResponse, TBody>(url, {
    ...options,
    method: "PATCH",
    body,
  })
}

export function apiDelete<TResponse>(
  url: string,
  options: Omit<
    ApiRequestOptions<never>,
    "method" | "body"
  > = {}
): Promise<TResponse> {
  return apiRequest<TResponse>(url, {
    ...options,
    method: "DELETE",
  })
}