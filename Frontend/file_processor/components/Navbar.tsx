'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"
import { cn } from "@/lib/utils"
import { Home, Settings, MessageSquare, FolderOpen, Play, FileText, AlertCircle } from 'lucide-react'

const Navbar = () => {
  const pathname = usePathname()

  const navLinks = [
    { href: '/', label: 'Home', icon: Home },
    { href: '/config', label: 'Configuration', icon: Settings },
    { href: '/prompt-management', label: 'Prompt Management', icon: MessageSquare },
    { href: '/file-management', label: 'File Management', icon: FolderOpen },
    { href: '/processing', label: 'Processing', icon: Play },
    { href: '/results', label: 'Results', icon: FileText },
    { href: '/errors', label: 'Errors', icon: AlertCircle },
  ]

  return (
    <NavigationMenu className="max-w-full w-full justify-center">
      <NavigationMenuList className="flex-wrap gap-2 p-4 bg-background border-b">
        {navLinks.map((link) => (
          <NavigationMenuItem key={link.href}>
            <Link href={link.href} legacyBehavior passHref>
              <NavigationMenuLink
                className={cn(
                  navigationMenuTriggerStyle(),
                  "flex items-center gap-2",
                  pathname === link.href
                    ? "bg-accent text-accent-foreground"
                    : "hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <link.icon className="w-4 h-4" />
                {link.label}
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  )
}

export default Navbar