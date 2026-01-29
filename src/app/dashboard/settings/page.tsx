'use client'

import { useState, useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Loader2, Plus, Trash2 } from 'lucide-react'

// Simple Hash (Client-side for migration compatibility - NOT SECURE for production apps)
async function hashPassword(password: string) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

export default function SettingsPage() {
    const supabase = createClient()
    const [users, setUsers] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [open, setOpen] = useState(false)
    const [creating, setCreating] = useState(false)

    // New User State
    const [newUser, setNewUser] = useState({
        email: "",
        password: "",
        role: "member"
    })

    useEffect(() => {
        fetchUsers()
    }, [])

    const fetchUsers = async () => {
        setLoading(true)
        const { data, error } = await supabase.from('users').select('*').order('created_at', { ascending: false })
        if (data) setUsers(data)
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
                allowed_tools: ["Dashboard", "ID Card", "Welcome Aboard", "Business Card"] // Default all for now
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

    // Note: Delete/Edit not requested but good to have. Keeping it simple for now.

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">Settings</h1>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle>User Management</CardTitle>
                        <CardDescription>Manage access to Trikon tools.</CardDescription>
                    </div>
                    <Dialog open={open} onOpenChange={setOpen}>
                        <DialogTrigger asChild>
                            <Button><Plus className="mr-2 h-4 w-4" /> Add User</Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>Create New User</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                                <div className="space-y-2">
                                    <Label>Email</Label>
                                    <Input value={newUser.email} onChange={e => setNewUser({ ...newUser, email: e.target.value })} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Password</Label>
                                    <Input type="password" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Role</Label>
                                    <Select value={newUser.role} onValueChange={v => setNewUser({ ...newUser, role: v })}>
                                        <SelectTrigger><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="member">Member</SelectItem>
                                            <SelectItem value="admin">Admin</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                                <Button className="w-full" onClick={handleCreateUser} disabled={creating}>
                                    {creating ? <Loader2 className="animate-spin h-4 w-4" /> : "Create User"}
                                </Button>
                            </div>
                        </DialogContent>
                    </Dialog>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Role</TableHead>
                                    <TableHead>Created At</TableHead>
                                    <TableHead className="text-right">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {users.map((user) => (
                                    <TableRow key={user.id}>
                                        <TableCell className="font-medium">{user.email}</TableCell>
                                        <TableCell>
                                            <span className={`px-2 py-1 rounded-full text-xs ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-700'}`}>
                                                {user.role}
                                            </span>
                                        </TableCell>
                                        <TableCell className="text-gray-500 text-sm">
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell className="text-right">
                                            <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50">
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    )}
                </CardContent>
            </Card>
        </div>
    )
}
