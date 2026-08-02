import axios from "axios"

import { env } from "@/config/env"
import { normalizeApiError } from "@/lib/api/errors"

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: env.apiTimeoutMs,

  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
  },

  /*
   * Keep this enabled because the backend authentication
   * architecture may use secure cookies for refresh/session
   * operations.
   */
  withCredentials: true,
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    return Promise.reject(normalizeApiError(error))
  }
)