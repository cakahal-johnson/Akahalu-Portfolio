import {
  NextResponse,
} from "next/server"

export const dynamic =
  "force-dynamic"

export async function GET() {
  return NextResponse.json(
    {
      status: "healthy",
      service: "portfolio-web",
    },
    {
      status: 200,
      headers: {
        "Cache-Control":
          "no-store",
      },
    }
  )
}