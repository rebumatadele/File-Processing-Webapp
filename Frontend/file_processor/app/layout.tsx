// app/layout.tsx
import './globals.css';
import { FC, ReactNode } from 'react';
import Navbar from '@/components/Navbar';
import { Toaster } from '@/components/ui/toaster';

interface LayoutProps {
  children: ReactNode;
}

export const metadata = {
  title: 'File Processor App', // Title for the browser tab
  description: 'Effortlessly process and manage your files with ease.', // Description for SEO
  // Removed viewport from metadata
};

export const viewport = {
  width: 'device-width',
  initialScale: 1.0,
};

const Layout: FC<LayoutProps> = ({ children }) => {
  const faviconSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="#14B8A6" viewBox="0 0 24 24" stroke="#0F766E">
      <path fill-rule="evenodd" clip-rule="evenodd" d="M3 6a3 3 0 013-3h4.586a2 2 0 011.414.586l1.414 1.414a2 2 0 001.414.586H18a3 3 0 013 3v9a3 3 0 01-3 3H6a3 3 0 01-3-3V6zm15 2H6a1 1 0 00-1 1v7a1 1 0 001 1h12a1 1 0 001-1V9a1 1 0 00-1-1z" />
    </svg>

  `;

  return (
    <html lang="en">
      <head>
        <title>File Processor App</title>
        <meta name="description" content="Effortlessly process and manage your files with ease." />
        <link rel="icon" type="image/svg+xml" href={`data:image/svg+xml,${encodeURIComponent(faviconSVG)}`} />
      </head>
      <body className="text-gray-900">
        <div className="mx-auto">
          <Navbar />
          <main className="container mx-auto p-4">{children}</main>
          <Toaster />
        </div>
      </body>
    </html>
  );
};

export default Layout;
