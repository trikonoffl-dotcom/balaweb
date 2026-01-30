'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { getCurrentUser } from '@/lib/auth'
import { createClient } from '@/lib/supabase/client'
import { getApiUrl } from '@/lib/api'
import {
    IconUsers,
    IconTools,
    IconActivity,
    IconShieldLock,
    IconCpu,
    IconUserCircle
} from '@tabler/icons-react'
import { Loader2 } from 'lucide-react'

export default function DashboardPage() {
    const supabase = createClient()
    const [user, setUser] = useState<any>(null)
    const [stats, setStats] = useState({
        totalUsers: 0,
        allowedToolsCount: 0,
        engineStatus: 'checking',
        engineLatency: 0
    })
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const loadDashboardData = async () => {
            setLoading(true)
            const profile = await getCurrentUser()
            setUser(profile)

            if (profile) {
                // Fetch Total Users if Admin
                if (profile.role === 'admin') {
                    const { count } = await supabase.from('users').select('*', { count: 'exact', head: true })
                    setStats(prev => ({ ...prev, totalUsers: count || 0 }))
                }

                // Count Allowed Tools (Only count actual tools, not Dashboard)
                const toolsCount = profile.allowed_tools?.filter((t: string) =>
                    t !== 'Dashboard' && t !== 'Settings'
                ).length || 0
                setStats(prev => ({ ...prev, allowedToolsCount: toolsCount }))

                // Check Engine Status
                try {
                    const start = Date.now()
                    const res = await fetch(getApiUrl('/api/health'))
                    const latency = Date.now() - start
                    setStats(prev => ({
                        ...prev,
                        engineStatus: res.ok ? 'online' : 'error',
                        engineLatency: latency
                    }))
                } catch (e) {
                    setStats(prev => ({ ...prev, engineStatus: 'error' }))
                }
            }
            setLoading(false)
        }
        loadDashboardData()
    }, [])

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
        )
    }

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-slate-800">Welcome Back, {user?.email?.split('@')[0]}</h1>
                <p className="text-slate-500 mt-1">Here is what's happening in your Trikon workspace.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* User Role Card */}
                <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium text-slate-600">Account Role</CardTitle>
                        <IconShieldLock className="h-5 w-5 text-purple-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold capitalize text-slate-800">{user?.role}</div>
                        <p className="text-xs text-slate-400 mt-1 flex items-center">
                            <IconUserCircle className="h-3 w-3 mr-1" /> Verified Account
                        </p>
                    </CardContent>
                </Card>

                {/* Available Tools Card */}
                <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium text-slate-600">Active Tools</CardTitle>
                        <IconTools className="h-5 w-5 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-slate-800">
                            {user?.role === 'admin' ? 'Unlimited' : stats.allowedToolsCount}
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                            {user?.role === 'admin' ? 'Master Access' : 'Authorized Toolset'}
                        </p>
                    </CardContent>
                </Card>

                {/* Engine Health Card */}
                <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                        <CardTitle className="text-sm font-medium text-slate-600">API Engine</CardTitle>
                        <IconCpu className="h-5 w-5 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-center gap-2">
                            <span className={`h-2.5 w-2.5 rounded-full ${stats.engineStatus === 'online' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                            <div className="text-2xl font-bold uppercase text-slate-800">{stats.engineStatus}</div>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                            {stats.engineLatency}ms response latency
                        </p>
                    </CardContent>
                </Card>

                {/* Admin Only: Total Users */}
                {user?.role === 'admin' && (
                    <Card className="border-slate-200 shadow-sm hover:shadow-md transition-all">
                        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                            <CardTitle className="text-sm font-medium text-slate-600">Total Teams</CardTitle>
                            <IconUsers className="h-5 w-5 text-orange-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-slate-800">{stats.totalUsers}</div>
                            <p className="text-xs text-slate-400 mt-1">Manageable user accounts</p>
                        </CardContent>
                    </Card>
                )}
            </div>

            <div className="mt-12">
                <div className="bg-slate-900 rounded-2xl p-8 text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
                    <div className="space-y-2">
                        <h2 className="text-2xl font-bold">Ready to get started?</h2>
                        <p className="text-slate-400 max-w-md">
                            Select a tool from the sidebar to begin generating professional documents and assets with AI optimization.
                        </p>
                    </div>
                    <div className="flex gap-4">
                        <div className="px-4 py-2 bg-slate-800 rounded-lg border border-slate-700 flex items-center gap-2">
                            <IconActivity className="h-4 w-4 text-blue-400" />
                            <span className="text-sm font-medium">System V2.1 Operational</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
