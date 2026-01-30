import { Checkbox } from "@/components/ui/checkbox"

const ALL_TOOLS = ["Dashboard", "ID Card", "Welcome Aboard", "Business Card", "AI BG Remover"]

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

        try {
            const { error } = await supabase
                .from('users')
                .update({ allowed_tools: selectedUser.allowed_tools })
                .eq('id', selectedUser.id)

            if (!error) {
                setAccessOpen(false)
                fetchUsers()
            }
        } catch (e) {
            console.error(e)
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
            <h1 className="text-3xl font-bold mb-6">Settings</h1>

            {/* User Access Dialog */}
            <Dialog open={accessOpen} onOpenChange={setAccessOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Manage Access: {selectedUser?.email}</DialogTitle>
                        <CardDescription>Select which tools this user can access.</CardDescription>
                    </DialogHeader>
                    <div className="py-4 space-y-4">
                        {ALL_TOOLS.map(tool => (
                            <div key={tool} className="flex items-center space-x-3">
                                <Checkbox
                                    id={tool}
                                    checked={selectedUser?.allowed_tools?.includes(tool)}
                                    onCheckedChange={() => toggleTool(tool)}
                                />
                                <Label htmlFor={tool} className="cursor-pointer">{tool}</Label>
                            </div>
                        ))}
                    </div>
                    <Button className="w-full" onClick={handleUpdateAccess} disabled={updatingAccess}>
                        {updatingAccess ? <Loader2 className="animate-spin h-4 w-4" /> : "Save Changes"}
                    </Button>
                </DialogContent>
            </Dialog>

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
                                    <TableHead>Allowed Tools</TableHead>
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
                                        <TableCell>
                                            <div className="flex flex-wrap gap-1 max-w-[300px]">
                                                {user.role === 'admin' ? (
                                                    <span className="text-xs text-gray-400">All Tools</span>
                                                ) : (
                                                    user.allowed_tools?.map((t: string) => (
                                                        <span key={t} className="bg-blue-50 text-blue-600 px-1.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-tight border border-blue-100">
                                                            {t}
                                                        </span>
                                                    ))
                                                )}
                                            </div>
                                        </TableCell>
                                        <TableCell className="text-right flex items-center justify-end gap-2">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                onClick={() => { setSelectedUser(user); setAccessOpen(true); }}
                                                disabled={user.role === 'admin'}
                                            >
                                                Edit Access
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                                                onClick={async () => {
                                                    if (confirm("Are you sure?")) {
                                                        await supabase.from('users').delete().eq('id', user.id)
                                                        fetchUsers()
                                                    }
                                                }}
                                            >
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
