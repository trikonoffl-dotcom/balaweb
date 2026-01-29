import Link from 'next/link'

export default function DashboardPage() {
    return (
        <div className="p-8">
            <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
            <p className="text-gray-600">Welcome to the Trikon Ecosystem.</p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <Link href="/dashboard/id-card" className="p-6 bg-white rounded-lg shadow border cursor-pointer hover:shadow-md transition">
                    <h3 className="text-xl font-semibold mb-2">🆔 ID Card Generator</h3>
                    <p className="text-sm text-gray-500">Generate professional ID cards with auto-crop.</p>
                </Link>
                <Link href="/dashboard/welcome" className="p-6 bg-white rounded-lg shadow border cursor-pointer hover:shadow-md transition">
                    <h3 className="text-xl font-semibold mb-2">🛳️ Welcome Aboard</h3>
                    <p className="text-sm text-gray-500">Create welcome assets for new employees.</p>
                </Link>
                <Link href="/dashboard/business-card" className="p-6 bg-white rounded-lg shadow border cursor-pointer hover:shadow-md transition">
                    <h3 className="text-xl font-semibold mb-2">📇 Business Card</h3>
                    <p className="text-sm text-gray-500">Craft high-fidelity business cards.</p>
                </Link>
                <Link href="/dashboard/settings" className="p-6 bg-white rounded-lg shadow border cursor-pointer hover:shadow-md transition">
                    <h3 className="text-xl font-semibold mb-2">⚙️ Settings</h3>
                    <p className="text-sm text-gray-500">Manage users and access.</p>
                </Link>
            </div>
        </div>
    )
}
