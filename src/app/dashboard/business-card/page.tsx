'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { getApiUrl } from '@/lib/api'
import { Loader2, Download, RefreshCw } from 'lucide-react'

// Office Addresses
const ADDRESSES = [
    "3/7 Meridian Place, Bella Vista NSW 2153, Australia",
    "Suite 208, 111 Overton Rd, Williams Landing VIC 3030, Australia",
    "Unit 3, 304 Montague Road, West End QLD 4101, Australia",
    "Suite 2, 161 Maitland Road, Mayfield NSW 2304, Australia",
    "Level 5, Suite 5, 221-229 Crown St, Wollongong NSW, Australia",
    "Level 5, Suite 5, 221-229 Crown St, Wollongong NSW 2500, Australia (Business Hub)",
    "Shop 4, 285 Windsor St, Richmond NSW 2753, Australia (Hawkesbury Business Hub)"
]

export default function BusinessCardPage() {
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)
    const [generating, setGenerating] = useState(false)

    const [formData, setFormData] = useState({
        template: "Trikon",
        first_name: "John",
        last_name: "Doe",
        title: "General Manager",
        phone_mobile: "0400 000 000",
        phone_office: "1300 TRIKON (874 566)",
        email: "john.doe@example.com",
        website: "www.trikon.com.au",
        address: ADDRESSES[0],
        address_line1: "",
        address_line2: ""
    })

    const timeoutRef = useRef<NodeJS.Timeout | null>(null)

    // Initial Address Split Logic
    useEffect(() => {
        splitAddress(formData.address)
    }, [])

    const splitAddress = (fullAddr: string) => {
        const parts = fullAddr.split(", ")
        let line1 = "", line2 = ""
        if (parts.length > 2 && (parts[0].length < 12 || ['suite', 'unit', 'level', 'shop'].some(x => parts[0].toLowerCase().includes(x)))) {
            line1 = `${parts[0]}, ${parts[1]}`
            line2 = parts.slice(2).join(", ")
        } else {
            line1 = parts[0]
            line2 = parts.slice(1).join(", ")
        }
        setFormData(prev => ({ ...prev, address_line1: line1, address_line2: line2, address: fullAddr }))
    }

    const handleChange = (key: string, value: any) => {
        // Special logic for Template defaults
        if (key === 'template') {
            const isTrikon = value === "Trikon"
            setFormData(prev => ({
                ...prev,
                template: value,
                website: isTrikon ? "www.trikon.com.au" : "metaweb.com.au",
                phone_office: isTrikon ? "1300 TRIKON (874 566)" : "1300 262 987"
            }))
        } else if (key === 'address') {
            splitAddress(value)
        } else {
            setFormData(prev => ({ ...prev, [key]: value }))
        }
    }

    // Debounced Preview
    useEffect(() => {
        if (timeoutRef.current) clearTimeout(timeoutRef.current)
        timeoutRef.current = setTimeout(() => {
            fetchPreview()
        }, 800)
        return () => clearTimeout(timeoutRef.current!)
    }, [formData])

    const fetchPreview = async () => {
        setLoading(true)
        const form = new FormData()
        Object.entries(formData).forEach(([key, val]) => form.append(key, String(val)))

        try {
            const res = await fetch(getApiUrl('/api/preview-business-card'), { method: 'POST', body: form })
            if (res.ok) {
                const blob = await res.blob()
                setPreviewUrl(URL.createObjectURL(blob))
            }
        } catch (e) { console.error(e) }
        finally { setLoading(false) }
    }

    const handleDownload = async () => {
        setGenerating(true)
        const form = new FormData()
        Object.entries(formData).forEach(([key, val]) => form.append(key, String(val)))

        try {
            const res = await fetch(getApiUrl('/api/generate-business-card'), { method: 'POST', body: form })
            if (res.ok) {
                const blob = await res.blob()
                const url = window.URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `BusinessCard_${formData.first_name}.pdf`
                document.body.appendChild(a)
                a.click()
                a.remove()
            }
        } catch (e) { console.error(e) }
        finally { setGenerating(false) }
    }

    return (
        <div className="container mx-auto p-6 max-w-6xl">
            <h1 className="text-3xl font-bold mb-6">Business Card Generator</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                    <Card>
                        <CardHeader><CardTitle>Card Configuration</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Template Style</Label>
                                <Select value={formData.template} onValueChange={v => handleChange('template', v)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="Trikon">Trikon</SelectItem>
                                        <SelectItem value="Metaweb">Metaweb</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader><CardTitle>Employee Info</CardTitle></CardHeader>
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
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader><CardTitle>Contact Details</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Mobile</Label>
                                    <Input value={formData.phone_mobile} onChange={e => handleChange('phone_mobile', e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Office Phone</Label>
                                    <Input value={formData.phone_office} onChange={e => handleChange('phone_office', e.target.value)} />
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label>Email</Label>
                                    <Input value={formData.email} onChange={e => handleChange('email', e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label>Website</Label>
                                    <Input value={formData.website} onChange={e => handleChange('website', e.target.value)} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader><CardTitle>Office Location</CardTitle></CardHeader>
                        <CardContent className="space-y-4">
                            <div className="space-y-2">
                                <Label>Select Address</Label>
                                <Select value={formData.address} onValueChange={v => handleChange('address', v)}>
                                    <SelectTrigger><SelectValue /></SelectTrigger>
                                    <SelectContent>
                                        {ADDRESSES.map(a => (
                                            <SelectItem key={a} value={a} className="text-xs">{a}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>
                            <div className="space-y-2">
                                <Label>Address Line 1 (Refine)</Label>
                                <Input value={formData.address_line1} onChange={e => handleChange('address_line1', e.target.value)} />
                            </div>
                            <div className="space-y-2">
                                <Label>Address Line 2 (Refine)</Label>
                                <Input value={formData.address_line2} onChange={e => handleChange('address_line2', e.target.value)} />
                            </div>
                        </CardContent>
                    </Card>
                </div>

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
                                <img src={previewUrl} alt="Card Preview" className="max-w-full h-auto shadow-xl rounded" />
                            ) : (
                                <div className="text-gray-400 text-sm flex flex-col items-center">
                                    <RefreshCw className="h-8 w-8 mb-2 opacity-20" />
                                    Generating Preview...
                                </div>
                            )}
                        </CardContent>
                        <div className="p-4 border-t bg-white rounded-b-lg">
                            <Button className="w-full" onClick={handleDownload} disabled={generating}>
                                {generating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Generating PDF...
                                    </>
                                ) : (
                                    <>
                                        <Download className="mr-2 h-4 w-4" /> Download PDF
                                    </>
                                )}
                            </Button>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    )
}
