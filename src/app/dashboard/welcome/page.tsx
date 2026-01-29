'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Loader2, Download, RefreshCw } from 'lucide-react'

export default function WelcomePage() {
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const [formData, setFormData] = useState({
        first_name: "John",
        last_name: "Doe",
        title: "Software Engineer",
        doj: "2026-01-12",
        use_auto_crop: true
    })

    const handleChange = (key: string, value: any) => {
        setFormData(prev => ({ ...prev, [key]: value }))
    }

    const handleGenerate = async () => {
        if (!file) return
        setLoading(true)

        const form = new FormData()
        form.append('file', file)
        Object.entries(formData).forEach(([key, val]) => {
            form.append(key, String(val))
        })

        try {
            const res = await fetch('/api/generate-welcome', {
                method: 'POST',
                body: form
            })

            if (res.ok) {
                const blob = await res.blob()
                const url = URL.createObjectURL(blob)
                setPreviewUrl(url)
            }
        } catch (e) {
            console.error("Failed", e)
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = () => {
        if (previewUrl) {
            const a = document.createElement('a')
            a.href = previewUrl
            a.download = `Welcome_${formData.first_name}.jpg`
            document.body.appendChild(a)
            a.click()
            a.remove()
        }
    }

    return (
        <div className="container mx-auto p-6 max-w-4xl">
            <h1 className="text-3xl font-bold mb-6">Welcome Aboard Generator</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                    <Card>
                        <CardHeader><CardTitle>Employee Details</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>First Name</Label>
                                    <Input value={formData.first_name} onChange={e => handleChange('first_name', e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Last Name</Label>
                                    <Input value={formData.last_name} onChange={e => handleChange('last_name', e.target.value)} />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Job Title</Label>
                                <Input value={formData.title} onChange={e => handleChange('title', e.target.value)} />
                            </div>
                            <div className="space-y-2">
                                <Label>Joining Date</Label>
                                <Input type="date" value={formData.doj} onChange={e => handleChange('doj', e.target.value)} />
                            </div>

                            <div className="space-y-2 pt-4 border-t">
                                <Label>Profile Photo</Label>
                                <Input
                                    type="file"
                                    accept="image/*"
                                    onChange={(e) => {
                                        if (e.target.files?.[0]) setFile(e.target.files[0])
                                    }}
                                />
                                <div className="flex items-center space-x-2 pt-2">
                                    <Checkbox
                                        id="auto_crop"
                                        checked={formData.use_auto_crop}
                                        onCheckedChange={(c) => handleChange('use_auto_crop', c)}
                                    />
                                    <Label htmlFor="auto_crop">Smart Auto-Crop</Label>
                                </div>
                            </div>

                            <Button className="w-full mt-4" onClick={handleGenerate} disabled={!file || loading}>
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating...
                                    </>
                                ) : (
                                    "Generate Welcome Image"
                                )}
                            </Button>
                        </CardContent>
                    </Card>
                </div>

                <div className="space-y-6">
                    <Card className="bg-slate-50 border-slate-200 h-full">
                        <CardHeader>
                            <CardTitle>Preview</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col items-center justify-center min-h-[400px]">
                            {previewUrl ? (
                                <div className="space-y-4 w-full">
                                    <img src={previewUrl} alt="Welcome Preview" className="w-full rounded shadow-lg" />
                                    <Button variant="outline" className="w-full" onClick={handleDownload}>
                                        <Download className="mr-2 h-4 w-4" /> Download Image
                                    </Button>
                                </div>
                            ) : (
                                <div className="text-gray-400 text-sm flex flex-col items-center">
                                    <RefreshCw className="h-8 w-8 mb-2 opacity-20" />
                                    Result will appear here
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
