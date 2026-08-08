"use client"

import {
  createContext,
  useContext,
} from "react"

import type {
  AuthenticatedUser,
} from "@/types/authentication"

type AdminSessionContextValue = {
  user: AuthenticatedUser
}

const AdminSessionContext =
  createContext<AdminSessionContextValue | null>(
    null
  )

type AdminSessionProviderProps = {
  user: AuthenticatedUser
  children: React.ReactNode
}

export function AdminSessionProvider({
  user,
  children,
}: AdminSessionProviderProps) {
  return (
    <AdminSessionContext.Provider
      value={{
        user,
      }}
    >
      {children}
    </AdminSessionContext.Provider>
  )
}

export function useAdminSession(): AdminSessionContextValue {
  const context =
    useContext(
      AdminSessionContext
    )

  if (!context) {
    throw new Error(
      "useAdminSession must be used inside AdminSessionProvider."
    )
  }

  return context
}