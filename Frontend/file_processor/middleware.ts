// src/middleware.ts

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token') || request.headers.get('Authorization')?.split(' ')[1];

  // Define the paths that don't require authentication
  const publicPaths = ['/', '/login', '/signup'];

  if (publicPaths.includes(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  if (!token) {
    // Redirect to login page if not authenticated
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

// Configure the matcher to include all routes except the public ones
export const config = {
  matcher: '/((?!api|_next/static|favicon.ico).*)',
};
