import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    const userToken = request.cookies.get('trikon_auth_token')?.value

    // Protect Dashboard
    if (request.nextUrl.pathname.startsWith('/dashboard') && !userToken) {
        return NextResponse.redirect(new URL('/login', request.url))
    }

    // Redirect /login if already logged in
    if (request.nextUrl.pathname === '/login' && userToken) {
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    return response
}

export const config = {
    matcher: [
        '/dashboard/:path*',
        '/login',
    ],
}
