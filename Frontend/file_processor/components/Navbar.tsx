'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Settings,
  MessageSquare,
  FolderOpen,
  Play,
  FileText,
  Menu,
  X,
  PercentIcon,
  AlertTriangle,
  User,
  LogOut,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useToast } from '@/hooks/use-toast';

const navItems = [
  { name: 'Configuration', href: '/config', icon: Settings },
  { name: 'Prompt Management', href: '/prompt-management', icon: MessageSquare },
  { name: 'File Management', href: '/file-management', icon: FolderOpen },
  { name: 'Processing', href: '/processing', icon: Play },
  { name: 'Batch Processing', href: '/claude_batch_processing', icon: Play },
  { name: 'Results', href: '/results', icon: FileText },
  { name: 'Error', href: '/errors', icon: AlertTriangle },
  { name: 'Usage', href: '/usage', icon: PercentIcon },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const pathname = usePathname();
  const { toast } = useToast();

  // Check authentication status on component mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setIsLoggedIn(false);
    toast({
      title: 'Success',
      description: 'Logged out successfully',
    });
  };

  const AuthButton = () =>
    isLoggedIn ? (
      <Button
        onClick={handleLogout}
        variant="ghost"
        className="text-muted-foreground hover:text-primary"
      >
        <LogOut className="w-4 h-4 mr-2" />
        Logout
      </Button>
    ) : (
      <div className="flex space-x-2">
        <Link href="/login">
          <Button variant="ghost" className="text-muted-foreground hover:text-primary">
            <User className="w-4 h-4 mr-2" />
            Login
          </Button>
        </Link>
        <Link href="/signup">
          <Button variant="ghost" className="text-muted-foreground hover:text-primary">
            <User className="w-4 h-4 mr-2" />
            Sign Up
          </Button>
        </Link>
      </div>
    );

  return (
    <nav className="bg-background border-b border-border sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <Link href="/" className="flex-shrink-0 flex items-center">
              <span className="text-2xl font-bold text-primary">AI File Processor</span>
            </Link>
          </div>
          <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-8">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="text-muted-foreground hover:text-primary">
                  <Menu className="w-4 h-4 mr-2" />
                  Menu
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {navItems.map((item) => (
                  <DropdownMenuItem key={item.name} asChild>
                    <Link
                      href={item.href}
                      className={`flex items-center px-4 py-2 text-sm ${
                        pathname === item.href ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    >
                      <item.icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <AuthButton />
          </div>
          <div className="flex items-center sm:hidden">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  className="inline-flex items-center justify-center p-2 rounded-md text-muted-foreground hover:text-primary hover:bg-primary/10 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary"
                >
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
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center px-4 py-2 text-sm ${
                        pathname === item.href ? 'text-primary' : 'text-muted-foreground'
                      }`}
                    >
                      <item.icon className="w-4 h-4 mr-2" />
                      {item.name}
                    </Link>
                  </DropdownMenuItem>
                ))}
                <DropdownMenuItem asChild>
                  <div className="px-4 py-2">
                    <AuthButton />
                  </div>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </nav>
  );
}
