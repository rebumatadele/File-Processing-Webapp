'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import { Settings, MessageSquare, FolderOpen, Play, FileText, Menu, X, PercentIcon, AlertTriangle } from 'lucide-react'
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const navItems = [
  { name: "Configuration", href: "/config", icon: Settings },
  { name: "Prompt Management", href: "/prompt-management", icon: MessageSquare },
  { name: "File Management", href: "/file-management", icon: FolderOpen },
  { name: "Processing", href: "/processing", icon: Play },
  { name: "Results", href: "/results", icon: FileText },
  { name: "Error", href: "/errors", icon: AlertTriangle },
  { name: "Usage", href: "/usage", icon: PercentIcon }
]

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()

  return (
    <nav className="bg-background border-b border-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-primary">AI File Processor</span>
            </Link>
          </div>
          <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={`inline-flex items-center px-1 pt-1 text-sm font-medium ${
                  pathname === item.href
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-muted-foreground hover:text-primary hover:border-primary'
                }`}
              >
                <item.icon className="w-4 h-4 mr-2" />
                {item.name}
              </Link>
            ))}
          </div>
          <div className="-mr-2 flex items-center sm:hidden">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="inline-flex items-center justify-center p-2 rounded-md text-muted-foreground hover:text-primary hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary">
                  <span className="sr-only">Open main menu</span>
                  {isOpen ? (
                    <X className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Menu className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                {navItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link
                      href={item.href}
                      className={`flex items-center px-4 py-2 text-sm ${
                        pathname === item.href ? 'text-primary' : 'text-muted-foreground'
                      }`}
                      onClick={() => setIsOpen(false)}
                    >
                      <item.icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>

      {/* Mobile menu, show/hide based on menu state */}
      <motion.div
        className="sm:hidden"
        initial={false}
        animate={isOpen ? "open" : "closed"}
        variants={{
          open: { opacity: 1, height: "auto" },
          closed: { opacity: 0, height: 0 }
        }}
      >
        <div className="pt-2 pb-3 space-y-1">
          {navItems.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                pathname === item.href
                  ? 'border-primary text-primary bg-primary/10'
                  : 'border-transparent text-muted-foreground hover:bg-primary/5 hover:border-primary hover:text-primary'
              }`}
              onClick={() => setIsOpen(false)}
            >
              <div className="flex items-center">
                <item.icon className="w-4 h-4 mr-2" />
                {item.name}
              </div>
            </Link>
          ))}
        </div>
      </motion.div>
    </nav>
  )
}