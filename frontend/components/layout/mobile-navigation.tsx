"use client"

import {
  Menu,
} from "lucide-react"
import Link from "next/link"
import {
  usePathname,
} from "next/navigation"
import {
  useState,
} from "react"

import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { siteConfig } from "@/config/site"
import { cn } from "@/lib/utils"

function MobileNavigation() {
  const pathname = usePathname()
  const [open, setOpen] = useState(false)

  return (
    <Sheet
      open={open}
      onOpenChange={setOpen}
    >
      <SheetTrigger asChild>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="md:hidden"
          aria-label="Open navigation menu"
        >
          <Menu
            className="size-5"
            aria-hidden="true"
          />
        </Button>
      </SheetTrigger>

      <SheetContent
        side="right"
        className="w-[88%] max-w-sm"
      >
        <SheetHeader className="border-b">
          <SheetTitle>
            {siteConfig.name}
          </SheetTitle>

          <SheetDescription>
            Navigate through the portfolio.
          </SheetDescription>
        </SheetHeader>

        <nav
          className="flex flex-1 flex-col gap-2 overflow-y-auto px-4 py-6"
          aria-label="Mobile navigation"
        >
          {siteConfig.navigation.map((item) => {
            const isActive =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href)

            return (
              <SheetClose
                key={item.href}
                asChild
              >
                <Link
                  href={item.href}
                  className={cn(
                    "flex min-h-11 items-center rounded-lg px-4 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  aria-current={
                    isActive ? "page" : undefined
                  }
                >
                  {item.label}
                </Link>
              </SheetClose>
            )
          })}

          <div className="mt-auto border-t pt-6">
            <SheetClose asChild>
              <Button
                asChild
                className="w-full"
              >
                <Link href="/contact">
                  Let&apos;s talk
                </Link>
              </Button>
            </SheetClose>
          </div>
        </nav>
      </SheetContent>
    </Sheet>
  )
}

export { MobileNavigation }