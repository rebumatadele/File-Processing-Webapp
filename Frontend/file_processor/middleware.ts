// src/middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Note: If you are using Next 13 App Router, ensure you have the right
// folder structure (e.g., `app/middleware.ts` or `src/middleware.ts`).

export function middleware(request: NextRequest) {
  // Grab token from either the cookie or the "Authorization" header
  // (whichever you have decided on in your app).
  const token =
    request.cookies.get('access_token')?.value ||
    request.headers.get('Authorization')?.split(' ')[1]

  // Define the paths that do NOT require authentication:
  //   - home page: '/'
  //   - login page: '/login'
  //   - signup page: '/signup'
  const publicPaths = ['/', '/login', '/signup']

  // If the user is requesting one of the public paths, just allow
  if (publicPaths.includes(request.nextUrl.pathname)) {
    return NextResponse.next()
  }

  // For all other pages (protected pages), we check if we have a token at all.
  if (!token) {
    // If no token is found, redirect to the login page
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // If there's a token in cookies/headers, let them through for now
  // (actual validity checking happens on the server or via interceptors).
  return NextResponse.next()
}

// Tell Next.js which routes the middleware should apply to.
// This example excludes /api, _next/static, and favicon.
export const config = {
  matcher: '/((?!api|_next/static|favicon.ico).*)',
}
