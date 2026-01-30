'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { getApiUrl } from '@/lib/api'
import {
    IconTools,
    IconAdjustmentsHorizontal,
    IconUsers,
    IconFiles,
    IconUpload,
    IconLayoutCards,
    IconId,
    IconShip
} from '@tabler/icons-react'
import { Plus, Trash2, Upload, FileType, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react'

// Shadcn UI Components
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table'
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from '@/components/ui/dialog'
import { Checkbox } from '@/components/ui/checkbox'

// Simple Hash (Client-side for migration compatibility - NOT SECURE for production apps)
async function hashPassword(password: string) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

const ALL_TOOLS = ["ID Card", "Welcome Aboard", "Business Card", "AI BG Remover", "Human Resource"]

export default function SettingsPage() {
    const supabase = createClient()
    const [users, setUsers] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [open, setOpen] = useState(false)
    const [creating, setCreating] = useState(false)
    const [accessOpen, setAccessOpen] = useState(false)
    const [selectedUser, setSelectedUser] = useState<any>(null)
    const [updatingAccess, setUpdatingAccess] = useState(false)

    // New User State
    const [newUser, setNewUser] = useState({
        email: "",
        password: "",
        role: "member"
    })

    // Tool Settings State
    const [genSettings, setGenSettings] = useState<any>(null)
    const [settingsLoading, setSettingsLoading] = useState(false)
    const [settingsSaving, setSettingsSaving] = useState(false)

    // Asset Management State
    const [assets, setAssets] = useState<{ templates: string[], fonts: string[] }>({ templates: [], fonts: [] })
    const [uploading, setUploading] = useState(false)
    const [activeTab, setActiveTab] = useState('users')

    useEffect(() => {
        fetchUsers()
        fetchGenSettings()
        fetchAssets()
    }, [])

    const fetchAssets = async () => {
        try {
            const res = await fetch(getApiUrl('/api/admin/assets'))
            if (res.ok) {
                const data = await res.json()
                setAssets(data)
            }
        } catch (e) {
            console.error("Failed to fetch assets", e)
        }
    }

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>, category: 'template' | 'font') => {
        const file = e.target.files?.[0]
        if (!file) return

        setUploading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('category', category)

        try {
            const res = await fetch(getApiUrl('/api/admin/upload-asset'), {
                method: 'POST',
                body: formData
            })
            if (res.ok) {
                alert(`${file.name} uploaded successfully!`)
                fetchAssets()
            } else {
                const err = await res.json()
                alert(`Upload failed: ${err.error}`)
            }
        } catch (err) {
            alert("Upload failed due to connection error")
        } finally {
            setUploading(false)
        }
    }

    const fetchGenSettings = async () => {
        setSettingsLoading(true)
        try {
            const res = await fetch(getApiUrl('/api/admin/settings'))
            if (res.ok) {
                const data = await res.json()
                setGenSettings(data)
            }
        } catch (e) {
            console.error("Failed to fetch settings", e)
        } finally {
            setSettingsLoading(false)
        }
    }

    const saveGenSettings = async () => {
        setSettingsSaving(true)
        try {
            const res = await fetch(getApiUrl('/api/admin/settings'), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(genSettings)
            })
            if (res.ok) {
                alert("Settings saved successfully!")
            } else {
                alert("Failed to save settings")
            }
        } catch (e) {
            console.error(e)
            alert("Save failed")
        } finally {
            setSettingsSaving(false)
        }
    }

    const fetchUsers = async () => {
        setLoading(true)
        console.log("Fetching fresh user list...")
        const { data, error } = await supabase.from('users').select('*').order('created_at', { ascending: false })

        if (error) {
            console.error("Error fetching users:", error)
        }

        if (data) {
            console.log(`Fetched ${data.length} users`)
            setUsers(data)
        }
        setLoading(false)
    }

    const handleCreateUser = async () => {
        if (!newUser.email || !newUser.password) return
        setCreating(true)

        try {
            const hash = await hashPassword(newUser.password)
            const { error } = await supabase.from('users').insert({
                email: newUser.email,
                password_hash: hash,
                role: newUser.role,
                allowed_tools: ALL_TOOLS // Default all for new users
            })

            if (!error) {
                setOpen(false)
                setNewUser({ email: "", password: "", role: "member" })
                fetchUsers()
            } else {
                alert("Failed to create user: " + error.message)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setCreating(false)
        }
    }

    const handleUpdateAccess = async () => {
        if (!selectedUser) return
        setUpdatingAccess(true)
        console.log("Updating user access/role:", selectedUser)

        try {
            const { error, data } = await supabase
                .from('users')
                .update({
                    allowed_tools: selectedUser.allowed_tools,
                    role: selectedUser.role
                })
                .eq('id', selectedUser.id)
                .select()

            if (!error) {
                console.log("Update success:", data)
                setAccessOpen(false)
                await fetchUsers()
            } else {
                console.error("Update error:", error)
                alert("Update failed: " + error.message)
            }
        } catch (e: any) {
            console.error("Critical update error:", e)
            alert("Error: " + e.message)
        } finally {
            setUpdatingAccess(false)
        }
    }

    const toggleTool = (tool: string) => {
        if (!selectedUser) return
        const current = selectedUser.allowed_tools || []
        const next = current.includes(tool)
            ? current.filter((t: string) => t !== tool)
            : [...current, tool]
        setSelectedUser({ ...selectedUser, allowed_tools: next })
    }

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-4xl font-black text-slate-900 tracking-tight">Admin Console</h1>
                    <p className="text-slate-500">Manage users, adjust generator layouts, and update brand assets.</p>
                </div>
                <div className="bg-blue-50 px-4 py-2 rounded-full border border-blue-100 flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                    <span className="text-xs font-bold text-blue-700 uppercase tracking-widest">Admin Mode</span>
                </div>
            </div>

            {/* Simple Tab Control */}
            <div className="flex gap-2 mb-8 bg-slate-100 p-1.5 rounded-xl w-fit border border-slate-200 shadow-inner">
                <Button
                    variant={activeTab === 'users' ? 'default' : 'ghost'}
                    onClick={() => setActiveTab('users')}
                    className="rounded-lg h-10 px-6 font-bold"
                >
                    <IconUsers className="mr-2 h-4 w-4" /> Users
                </Button>
                <Button
                    variant={activeTab === 'layout' ? 'default' : 'ghost'}
                    onClick={() => setActiveTab('layout')}
                    className="rounded-lg h-10 px-6 font-bold"
                >
                    <IconAdjustmentsHorizontal className="mr-2 h-4 w-4" /> Tool Config
                </Button>
                <Button
                    variant={activeTab === 'assets' ? 'default' : 'ghost'}
                    onClick={() => setActiveTab('assets')}
                    className="rounded-lg h-10 px-6 font-bold"
                >
                    <IconFiles className="mr-2 h-4 w-4" /> Asset Manager
                </Button>
            </div>

            {/* UI Content Based on Switch */}
            {activeTab === 'users' && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <Card className="shadow-xl border-slate-200 overflow-hidden">
                        <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between py-6">
                            <div>
                                <CardTitle className="text-2xl font-black">User Access Control</CardTitle>
                                <CardDescription>Provision accounts and manage tool-level permissions.</CardDescription>
                            </div>
                            <Dialog open={open} onOpenChange={setOpen}>
                                <DialogTrigger asChild>
                                    <Button className="bg-slate-900 shadow-lg"><Plus className="mr-2 h-4 w-4" /> Provision New User</Button>
                                </DialogTrigger>
                                <DialogContent className="sm:max-w-[425px]">
                                    <DialogHeader>
                                        <DialogTitle className="text-2xl font-black">Add Team Member</DialogTitle>
                                        <CardDescription>Accounts created here gain instant access to Trikon Tools.</CardDescription>
                                    </DialogHeader>
                                    <div className="space-y-4 py-4">
                                        <div className="space-y-2">
                                            <Label className="font-bold">Work Email</Label>
                                            <Input placeholder="name@trikon.com" value={newUser.email} onChange={e => setNewUser({ ...newUser, email: e.target.value })} />
                                        </div>
                                        <div className="space-y-2">
                                            <Label className="font-bold">Initial Password</Label>
                                            <Input type="password" placeholder="••••••••" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} />
                                        </div>
                                        <div className="space-y-2">
                                            <Label className="font-bold">Permission Grade</Label>
                                            <Select value={newUser.role} onValueChange={v => setNewUser({ ...newUser, role: v })}>
                                                <SelectTrigger className="w-full font-medium">
                                                    <SelectValue />
                                                </SelectTrigger>
                                                <SelectContent>
                                                    <SelectItem value="member">Standard Member</SelectItem>
                                                    <SelectItem value="admin">System Administrator</SelectItem>
                                                </SelectContent>
                                            </Select>
                                        </div>
                                        <Button className="w-full h-11 text-lg font-bold bg-blue-600 hover:bg-blue-700 mt-2" onClick={handleCreateUser} disabled={creating}>
                                            {creating ? <Loader2 className="animate-spin h-5 w-5" /> : "Verify & Create"}
                                        </Button>
                                    </div>
                                </DialogContent>
                            </Dialog>
                        </CardHeader>
                        <CardContent className="p-0">
                            {loading ? (
                                <div className="flex flex-col items-center justify-center p-20 text-slate-400 gap-4">
                                    <Loader2 className="animate-spin h-10 w-10 text-blue-500" />
                                    <p className="font-bold uppercase tracking-widest text-xs">Syncing user directory...</p>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader className="bg-slate-50/80 border-b">
                                        <TableRow>
                                            <TableHead className="font-bold text-slate-800 py-4 px-6">Email Address</TableHead>
                                            <TableHead className="font-bold text-slate-800 py-4">Auth Level</TableHead>
                                            <TableHead className="font-bold text-slate-800 py-4">Tool Access Matrix</TableHead>
                                            <TableHead className="text-right py-4 px-6"></TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {users.map((user) => (
                                            <TableRow key={user.id} className="hover:bg-slate-50/50 transition-colors group">
                                                <TableCell className="font-bold text-slate-700 py-4 px-6">{user.email}</TableCell>
                                                <TableCell className="py-4">
                                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${user.role === 'admin' ? 'bg-indigo-100 text-indigo-700 border border-indigo-200' : 'bg-slate-100 text-slate-600 border border-slate-200'}`}>
                                                        {user.role}
                                                    </span>
                                                </TableCell>
                                                <TableCell className="py-4">
                                                    <div className="flex flex-wrap gap-1.5 max-w-[400px]">
                                                        {user.role === 'admin' ? (
                                                            <span className="text-[10px] font-bold text-slate-400 italic">Full Unrestricted Access</span>
                                                        ) : (
                                                            user.allowed_tools?.map((t: string) => (
                                                                <span key={t} className="bg-white text-blue-700 px-2 py-0.5 rounded text-[10px] font-bold border border-blue-200 shadow-sm">
                                                                    {t}
                                                                </span>
                                                            )) || <span className="text-xs text-red-400">No tools assigned</span>
                                                        )}
                                                    </div>
                                                </TableCell>
                                                <TableCell className="text-right py-4 px-6">
                                                    <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <Button variant="outline" size="sm" className="font-bold h-8 border-slate-300" onClick={() => { setSelectedUser(user); setAccessOpen(true); }}>
                                                            Manage
                                                        </Button>
                                                        <Button variant="ghost" size="icon" className="h-8 w-8 text-red-400 hover:text-red-700 hover:bg-red-50" onClick={async () => {
                                                            if (confirm(`Revoke all access for ${user.email}?`)) {
                                                                const { error } = await supabase.from('users').delete().eq('id', user.id)
                                                                if (!error) { setUsers(prev => prev.filter(u => u.id !== user.id)); fetchUsers(); }
                                                            }
                                                        }}>
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </div>
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </div>
            )}

            {activeTab === 'layout' && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    {genSettings ? (
                        <div className="space-y-6">
                            <Card className="shadow-2xl border-t-4 border-t-blue-600">
                                <CardHeader className="border-b pb-6">
                                    <div className="flex items-center justify-between">
                                        <CardTitle className="text-2xl font-black">Layout & Design Settings</CardTitle>
                                        <Button
                                            className="bg-blue-600 hover:bg-blue-700 font-black h-12 px-8 shadow-xl"
                                            onClick={saveGenSettings}
                                            disabled={settingsSaving}
                                        >
                                            {settingsSaving ? <><Loader2 className="animate-spin mr-2" /> Saving...</> : "Publish Global Changes"}
                                        </Button>
                                    </div>
                                    <CardDescription>Fine-tune typography, photo placements, and auto-crop behavior.</CardDescription>
                                </CardHeader>
                                <CardContent className="p-8 space-y-12">
                                    {/* ID Card Block */}
                                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
                                        <div className="lg:col-span-1 border-r pr-8">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-blue-100 rounded-lg text-blue-700"><IconId className="h-6 w-6" /></div>
                                                <h3 className="text-xl font-black">ID Cards</h3>
                                            </div>
                                            <p className="text-sm text-slate-500 italic">Adjust fonts, photo coordinates, and default template.</p>
                                        </div>
                                        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="space-y-4">
                                                <Label className="text-xs font-black uppercase tracking-tighter text-slate-400">Primary Template</Label>
                                                <Select value={genSettings.id_card.template_path.split(/[\\/]/).pop()} onValueChange={v => {
                                                    const next = { ...genSettings };
                                                    next.id_card.template_path = v; // Or handle full path mapping if needed
                                                    setGenSettings(next);
                                                }}>
                                                    <SelectTrigger><SelectValue placeholder="Select template file" /></SelectTrigger>
                                                    <SelectContent>
                                                        {assets.templates.filter(f => f.toLowerCase().includes('id') || f.toLowerCase().includes('name')).map(f => (
                                                            <SelectItem key={f} value={f}>{f}</SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <Label className="text-xs font-black uppercase text-slate-400">Photo X (mm)</Label>
                                                    <Input type="number" step="0.1" value={genSettings.id_card.photo_pos[0]} onChange={e => {
                                                        const next = { ...genSettings }; next.id_card.photo_pos[0] = parseFloat(e.target.value); setGenSettings(next);
                                                    }} />
                                                </div>
                                                <div className="space-y-2">
                                                    <Label className="text-xs font-black uppercase text-slate-400">Photo Y (mm)</Label>
                                                    <Input type="number" step="0.1" value={genSettings.id_card.photo_pos[1]} onChange={e => {
                                                        const next = { ...genSettings }; next.id_card.photo_pos[1] = parseFloat(e.target.value); setGenSettings(next);
                                                    }} />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Welcome Block */}
                                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 border-t pt-12">
                                        <div className="lg:col-span-1 border-r pr-8">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-orange-100 rounded-lg text-orange-700"><IconShip className="h-6 w-6" /></div>
                                                <h3 className="text-xl font-black">Welcome</h3>
                                            </div>
                                            <p className="text-sm text-slate-500 italic">Position names and welcome photo overlays.</p>
                                        </div>
                                        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="space-y-4">
                                                <Label className="text-xs font-black uppercase tracking-tighter text-slate-400">Graphic Template</Label>
                                                <Select value={genSettings.welcome_aboard.template_path.split(/[\\/]/).pop()} onValueChange={v => {
                                                    const next = { ...genSettings };
                                                    next.welcome_aboard.template_path = v;
                                                    setGenSettings(next);
                                                }}>
                                                    <SelectTrigger><SelectValue placeholder="Select graphic file" /></SelectTrigger>
                                                    <SelectContent>
                                                        {assets.templates.filter(f => f.toLowerCase().includes('welcome')).map(f => (
                                                            <SelectItem key={f} value={f}>{f}</SelectItem>
                                                        ))}
                                                    </SelectContent>
                                                </Select>
                                            </div>
                                            <div className="grid grid-cols-2 gap-4">
                                                <div className="space-y-2">
                                                    <Label className="text-xs font-black uppercase text-slate-400">Text X (pos)</Label>
                                                    <Input type="number" value={genSettings.welcome_aboard.first_name_pos[0]} onChange={e => {
                                                        const next = { ...genSettings }; next.welcome_aboard.first_name_pos[0] = parseInt(e.target.value); setGenSettings(next);
                                                    }} />
                                                </div>
                                                <div className="space-y-2">
                                                    <Label className="text-xs font-black uppercase text-slate-400">Text Y (baseline)</Label>
                                                    <Input type="number" value={genSettings.welcome_aboard.first_name_pos[1]} onChange={e => {
                                                        const next = { ...genSettings }; next.welcome_aboard.first_name_pos[1] = parseInt(e.target.value); setGenSettings(next);
                                                    }} />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* AI Block */}
                                    <div className="grid grid-cols-1 lg:grid-cols-4 gap-12 border-t pt-12">
                                        <div className="lg:col-span-1 border-r pr-8">
                                            <div className="flex items-center gap-3 mb-2">
                                                <div className="p-2 bg-purple-100 rounded-lg text-purple-700"><IconTools className="h-6 w-6" /></div>
                                                <h3 className="text-xl font-black">AI & Cropping</h3>
                                            </div>
                                            <p className="text-sm text-slate-500 italic">Adjust facial recognition headroom and aspects.</p>
                                        </div>
                                        <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-2 gap-8">
                                            <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
                                                <h4 className="text-xs font-bold uppercase text-blue-600 tracking-widest">ID Card Auto-Crop</h4>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="space-y-1">
                                                        <Label className="text-[10px] font-bold text-slate-400">Ratio (W/H)</Label>
                                                        <Input type="number" step="0.1" value={genSettings.auto_crop.id_card.target_ratio} onChange={e => {
                                                            const next = { ...genSettings }; next.auto_crop.id_card.target_ratio = parseFloat(e.target.value); setGenSettings(next);
                                                        }} />
                                                    </div>
                                                    <div className="space-y-1">
                                                        <Label className="text-[10px] font-bold text-slate-400">Headroom</Label>
                                                        <Input type="number" step="0.1" value={genSettings.auto_crop.id_card.top_headroom} onChange={e => {
                                                            const next = { ...genSettings }; next.auto_crop.id_card.top_headroom = parseFloat(e.target.value); setGenSettings(next);
                                                        }} />
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 space-y-4">
                                                <h4 className="text-xs font-bold uppercase text-orange-600 tracking-widest">Welcome Auto-Crop</h4>
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div className="space-y-1">
                                                        <Label className="text-[10px] font-bold text-slate-400">Ratio (W/H)</Label>
                                                        <Input type="number" step="0.1" value={genSettings.auto_crop.welcome.target_ratio} onChange={e => {
                                                            const next = { ...genSettings }; next.auto_crop.welcome.target_ratio = parseFloat(e.target.value); setGenSettings(next);
                                                        }} />
                                                    </div>
                                                    <div className="space-y-1">
                                                        <Label className="text-[10px] font-bold text-slate-400">Headroom</Label>
                                                        <Input type="number" step="0.1" value={genSettings.auto_crop.welcome.top_headroom} onChange={e => {
                                                            const next = { ...genSettings }; next.auto_crop.welcome.top_headroom = parseFloat(e.target.value); setGenSettings(next);
                                                        }} />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    ) : (
                        <div className="h-64 flex items-center justify-center text-slate-400 italic">Syncing system parameters...</div>
                    )}
                </div>
            )}

            {activeTab === 'assets' && (
                <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card className="shadow-lg border-slate-200">
                            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between py-6">
                                <div>
                                    <CardTitle className="text-xl font-black">Template Files</CardTitle>
                                    <CardDescription>PDFs and Images used for generation.</CardDescription>
                                </div>
                                <div className="relative cursor-pointer group">
                                    <Input
                                        type="file"
                                        accept=".pdf,.jpg,.jpeg,.png"
                                        className="absolute inset-0 opacity-0 cursor-pointer z-10"
                                        onChange={e => handleUpload(e, 'template')}
                                        disabled={uploading}
                                    />
                                    <Button size="sm" variant="outline" className="group-hover:bg-slate-50">
                                        {uploading ? <Loader2 className="animate-spin h-4 w-4" /> : <IconUpload className="h-4 w-4 mr-2" />}
                                        Upload New
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent className="p-0 max-h-[500px] overflow-y-auto">
                                <Table>
                                    <TableBody>
                                        {assets.templates.length === 0 ? (
                                            <TableRow><TableCell className="text-center py-20 text-slate-400 italic">No templates found in /Templates folder.</TableCell></TableRow>
                                        ) : (
                                            assets.templates.map(file => (
                                                <TableRow key={file} className="group h-12">
                                                    <TableCell className="pl-6">
                                                        <div className="flex items-center gap-3">
                                                            <div className="p-1.5 bg-blue-50 text-blue-500 rounded border border-blue-100"><IconFiles className="h-4 w-4" /></div>
                                                            <span className="font-bold text-slate-700 text-sm truncate max-w-[300px]">{file}</span>
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="text-right pr-6 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <span className="text-[10px] font-black p-1 bg-slate-100 rounded text-slate-400 uppercase tracking-tighter">System Asset</span>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </CardContent>
                        </Card>

                        <Card className="shadow-lg border-slate-200">
                            <CardHeader className="bg-slate-50/50 border-b flex flex-row items-center justify-between py-6">
                                <div>
                                    <CardTitle className="text-xl font-black">Font Library</CardTitle>
                                    <CardDescription>TTF/OTF files for custom typography.</CardDescription>
                                </div>
                                <div className="relative cursor-pointer group">
                                    <Input
                                        type="file"
                                        accept=".ttf,.otf"
                                        className="absolute inset-0 opacity-0 cursor-pointer z-10"
                                        onChange={e => handleUpload(e, 'font')}
                                        disabled={uploading}
                                    />
                                    <Button size="sm" variant="outline" className="group-hover:bg-slate-50">
                                        {uploading ? <Loader2 className="animate-spin h-4 w-4" /> : <IconUpload className="h-4 w-4 mr-2" />}
                                        Add Font
                                    </Button>
                                </div>
                            </CardHeader>
                            <CardContent className="p-0 max-h-[500px] overflow-y-auto">
                                <Table>
                                    <TableBody>
                                        {assets.fonts.length === 0 ? (
                                            <TableRow><TableCell className="text-center py-20 text-slate-400 italic">No custom fonts detected in /fonts folder.</TableCell></TableRow>
                                        ) : (
                                            assets.fonts.map(file => (
                                                <TableRow key={file} className="group h-12">
                                                    <TableCell className="pl-6">
                                                        <div className="flex items-center gap-3">
                                                            <div className="p-1.5 bg-yellow-50 text-yellow-600 rounded border border-yellow-100"><FileType className="h-4 w-4" /></div>
                                                            <span className="font-bold text-slate-700 text-sm truncate max-w-[300px]">{file}</span>
                                                        </div>
                                                    </TableCell>
                                                    <TableCell className="text-right pr-6 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <span className="text-[10px] font-black p-1 bg-slate-100 rounded text-slate-400 uppercase tracking-tighter">Verified Font</span>
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        )}
                                    </TableBody>
                                </Table>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            )}
        </div>
    )
}
