// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Grab token from either the cookie or the "Authorization" header
  const token =
    request.cookies.get('access_token')?.value ||
    request.headers.get('Authorization')?.split(' ')[1]
  
  const publicPaths = ['/', '/login', '/signup']

  if (publicPaths.includes(request.nextUrl.pathname)) {
    return NextResponse.next()
  }

  // For all other pages (protected pages), we check if we have a token at all.
  if (!token) {
    // If no token is found, redirect to the login page
    return NextResponse.redirect(new URL('/login', request.url))
  }
  return NextResponse.next()
}
export const config = {
  matcher: '/((?!api|_next/static|favicon.ico).*)',
}
