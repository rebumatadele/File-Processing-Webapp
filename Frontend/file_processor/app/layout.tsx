// app/layout.tsx
import './globals.css';
import { FC, ReactNode } from 'react';
import Navbar from '@/components/Navbar';
import { Toaster } from '@/components/ui/toaster';

interface LayoutProps {
  children: ReactNode;
}

const Layout: FC<LayoutProps> = ({ children }) => {
  return (
    <html lang="en">
      <body className="bg-gray-100 text-gray-900">
          <Navbar />
          <main className="container mx-auto p-4">
            {children}
          </main>
          <Toaster />
      </body>
    </html>
  );
};

export default Layout;
