import { createClient } from './supabase/client'

export async function getCurrentUser() {
    const supabase = createClient()

    // Get token from cookie
    const cookies = document.cookie.split('; ')
    const tokenCookie = cookies.find(row => row.startsWith('trikon_auth_token='))
    const userId = tokenCookie ? tokenCookie.split('=')[1] : null

    if (!userId) return null

    const { data: user, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', userId)
        .single()

    if (error || !user) return null
    return user
}
