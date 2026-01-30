'use client'

import { Header } from "@/components/ui/header"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useEffect } from "react"
import { IconLayoutDashboard, IconId, IconShip, IconBusinessplan, IconSettings, IconLogout, IconPhotoEdit } from "@tabler/icons-react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { getCurrentUser } from "@/lib/auth"

const sidebarItems = [
    { name: "Dashboard", href: "/dashboard", icon: IconLayoutDashboard },
    { name: "ID Card", href: "/dashboard/id-card", icon: IconId },
    { name: "Welcome Aboard", href: "/dashboard/welcome", icon: IconShip },
    { name: "Business Card", href: "/dashboard/business-card", icon: IconBusinessplan },
    { name: "AI BG Remover", href: "/dashboard/bg-remover", icon: IconPhotoEdit },
    { name: "Settings", href: "/dashboard/settings", icon: IconSettings },
]

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname()
    const [user, setUser] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchUser = async () => {
            const profile = await getCurrentUser()
            setUser(profile)
            setLoading(false)
        }
        fetchUser()
    }, [])

    const filteredItems = sidebarItems.filter(item => {
        if (!user) return false
        if (user.role === 'admin') return true

        // Settings only for Admins
        if (item.name === "Settings") return false

        // Check allowed_tools array
        if (user.allowed_tools && Array.isArray(user.allowed_tools)) {
            return user.allowed_tools.includes(item.name)
        }

        return false
    })

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center bg-gray-50"><Loader2 className="animate-spin text-blue-600" /></div>
    }

    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            <Header />
            <div className="flex flex-1">
                {/* Sidebar */}
                <aside className="w-64 bg-white border-r hidden md:block">
                    <nav className="p-4 space-y-1">
                        {filteredItems.map((item) => {
                            const isActive = pathname === item.href
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                                        isActive
                                            ? "bg-blue-50 text-blue-700"
                                            : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                                    )}
                                >
                                    <item.icon className="h-4 w-4" />
                                    {item.name}
                                </Link>
                            )
                        })}
                    </nav>
                    <div className="p-4 border-t mt-auto">
                        <Link
                            href="/login"
                            onClick={() => document.cookie = "trikon_auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;"}
                            className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-red-600 hover:bg-red-50"
                        >
                            <IconLogout className="h-4 w-4" />
                            Logout
                        </Link>
                    </div>
                </aside>

                {/* Main Content */}
                <main className="flex-1 p-0 overflow-auto">
                    {children}
                </main>
            </div>
        </div>
    )
}
