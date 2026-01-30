'use client'

import { useState, useEffect, useRef } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { getApiUrl } from '@/lib/api'
import { Loader2, Download, RefreshCw, Image as ImageIcon } from 'lucide-react'

// Office Addresses (Moved from Python)
const OFFICES = {
    "Chennai": "Centre Point 3 , 7th Floor\n2/4 Mount Ponnamallee High Road\nManapakkam, Porur, Chennai 600089",
    "Ahmedabad": "COLONNADE-2, 1105, 11th Floor\nbehind Rajpath Rangoli Road\nBodakdev, Ahmedabad, Gujarat 380059"
}

export default function IDCardPage() {
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [generating, setGenerating] = useState(false)

    // Form State
    const [formData, setFormData] = useState({
        first_name: "Bragadeesh",
        last_name: "Sundararajan",
        title: "AI Prompt Engineer",
        id_number: "TRC00049",
        doj: "2025-11-17",
        emergency_no: "9566191956",
        blood_group: "O+",
        office_choice: "Chennai",
        office_address: OFFICES["Chennai"],

        // Adjustments
        scale: 1.0,
        x_offset: 0,
        y_offset: 0,
        use_auto_crop: true,
        use_ai_removal: true
    })

    const timeoutRef = useRef<NodeJS.Timeout | null>(null)

    // Handle inputs
    const handleChange = (key: string, value: any) => {
        setFormData(prev => ({ ...prev, [key]: value }))

        // Update address if office changes
        if (key === 'office_choice') {
            setFormData(prev => ({ ...prev, office_choice: value, office_address: OFFICES[value as keyof typeof OFFICES] }))
        }
    }

    // Auto-preview removed as per user request
    // User must click "Generate Preview" button


    const fetchPreview = async () => {
        if (!file) return
        setLoading(true)

        const form = new FormData()
        form.append('file', file)

        Object.entries(formData).forEach(([key, val]) => {
            form.append(key, String(val))
        })

        try {
            const res = await fetch(getApiUrl('/api/preview-id-card'), {
                method: 'POST',
                body: form
            })

            if (res.ok) {
                const blob = await res.blob()
                const url = URL.createObjectURL(blob)
                setPreviewUrl(url)
            }
        } catch (e) {
            console.error("Preview failed", e)
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = async () => {
        if (!file) return;
        setGenerating(true)

        const form = new FormData()
        form.append('file', file)
        Object.entries(formData).forEach(([key, val]) => {
            form.append(key, String(val))
        })

        try {
            const res = await fetch(getApiUrl('/api/generate-id-card'), {
                method: 'POST',
                body: form
            })

            if (res.ok) {
                const blob = await res.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `ID_Card_${formData.id_number}.pdf`
                document.body.appendChild(a)
                a.click()
                a.remove()
            }
        } catch (e) {
            console.error(e)
        } finally {
            setGenerating(false)
        }
    }

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">ID Card Generator</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Form Controls */}
                <div className="space-y-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Front Side Details</CardTitle>
                        </CardHeader>
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
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>ID Number</Label>
                                    <Input value={formData.id_number} onChange={e => handleChange('id_number', e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Joining Date</Label>
                                    <Input type="date" value={formData.doj} onChange={e => handleChange('doj', e.target.value)} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>Photo & Adjustments</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-1">
                                <Input
                                    type="file"
                                    accept=".jpg,.jpeg,.png,.webp,.avif"
                                    onChange={(e) => {
                                        if (e.target.files?.[0]) {
                                            setFile(e.target.files[0])
                                        }
                                    }}
                                />
                                <p className="text-[10px] text-muted-foreground px-1">
                                    Supported: JPG, PNG, WebP, AVIF
                                </p>
                            </div>

                            <div className="flex items-center space-x-4">
                                <div className="flex items-center space-x-2">
                                    <Checkbox
                                        id="bg_removal"
                                        checked={formData.use_ai_removal}
                                        onCheckedChange={(c) => handleChange('use_ai_removal', c)}
                                    />
                                    <Label htmlFor="bg_removal">Remove Background</Label>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <Checkbox
                                        id="auto_crop"
                                        checked={formData.use_auto_crop}
                                        onCheckedChange={(c) => handleChange('use_auto_crop', c)}
                                    />
                                    <Label htmlFor="auto_crop">Smart Auto-Crop</Label>
                                </div>
                            </div>

                            {!formData.use_auto_crop && (
                                <div className="space-y-4 pt-4 border-t">
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Scale ({formData.scale.toFixed(2)}x)</Label>
                                        </div>
                                        <Slider
                                            value={[formData.scale]}
                                            min={0.5} max={3.0} step={0.05}
                                            onValueChange={([v]) => handleChange('scale', v)}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>X Offset ({formData.x_offset}px)</Label>
                                        </div>
                                        <Slider
                                            value={[formData.x_offset]}
                                            min={-100} max={100} step={1}
                                            onValueChange={([v]) => handleChange('x_offset', v)}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <div className="flex justify-between">
                                            <Label>Y Offset ({formData.y_offset}px)</Label>
                                        </div>
                                        <Slider
                                            value={[formData.y_offset]}
                                            min={-100} max={100} step={1}
                                            onValueChange={([v]) => handleChange('y_offset', v)}
                                        />
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>

                {/* Preview & Back Side */}
                <div className="space-y-6">
                    <Card className="bg-slate-50 border-slate-200">
                        <CardHeader>
                            <CardTitle className="flex justify-between items-center">
                                Preview
                                {loading && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="flex justify-center items-center min-h-[300px] bg-slate-100/50 rounded-lg p-4">
                            {previewUrl ? (
                                <img src={previewUrl} alt="ID Preview" className="max-w-full h-auto shadow-xl rounded-lg" />
                            ) : (
                                <div className="text-gray-400 text-sm flex flex-col items-center">
                                    <ImageIcon className="h-8 w-8 mb-2 opacity-20" />
                                    Click "Generate Preview" to see ID card
                                </div>
                            )}
                        </CardContent>
                        <div className="p-4 border-t bg-white rounded-b-lg space-y-3">
                            <Button
                                className="w-full bg-slate-800 hover:bg-slate-900"
                                onClick={fetchPreview}
                                disabled={!file || loading}
                            >
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating Preview...
                                    </>
                                ) : (
                                    <>
                                        <RefreshCw className="mr-2 h-4 w-4" /> Generate Preview
                                    </>
                                )}
                            </Button>

                            <Button className="w-full" onClick={handleDownload} disabled={!file || generating}>
                                {generating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating PDF...
                                    </>
                                ) : (
                                    <>
                                        <Download className="mr-2 h-4 w-4" /> Download ID Card
                                    </>
                                )}
                            </Button>
                        </div>
                    </Card>

                    <Card>
                        <CardHeader><CardTitle>Back Side</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Emergency No</Label>
                                    <Input value={formData.emergency_no} onChange={e => handleChange('emergency_no', e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Blood Group</Label>
                                    <Select value={formData.blood_group} onValueChange={v => handleChange('blood_group', v)}>
                                        <SelectTrigger><SelectValue /></SelectTrigger>
                                        <SelectContent>
                                            {["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"].map(g => (
                                                <SelectItem key={g} value={g}>{g}</SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            <div className="space-y-2">
                                <Label>Office Address</Label>
                                <Select value={formData.office_choice} onValueChange={v => handleChange('office_choice', v)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Chennai">Chennai</SelectItem>
                                        <SelectItem value="Ahmedabad">Ahmedabad</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    )
}
