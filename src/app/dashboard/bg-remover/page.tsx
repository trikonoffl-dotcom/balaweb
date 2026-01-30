"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2, Download, Upload, Image as ImageIcon } from 'lucide-react'
import { getApiUrl } from '@/lib/api'

export default function BgRemoverPage() {
    const [file, setFile] = useState<File | null>(null)
    const [previewUrl, setPreviewUrl] = useState<string | null>(null)
    const [processedUrl, setProcessedUrl] = useState<string | null>(null)
    const [loading, setLoading] = useState(false)

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            const f = e.target.files[0]
            setFile(f)
            setPreviewUrl(URL.createObjectURL(f))
            setProcessedUrl(null)
        }
    }

    const handleRemoveBg = async () => {
        if (!file) return
        setLoading(true)

        const form = new FormData()
        form.append('file', file)

        try {
            const res = await fetch(getApiUrl('/api/remove-bg'), {
                method: 'POST',
                body: form
            })

            if (res.ok) {
                const blob = await res.blob()
                setProcessedUrl(URL.createObjectURL(blob))
            }
        } catch (e) {
            console.error("BG Removal failed", e)
        } finally {
            setLoading(false)
        }
    }

    const handleDownload = () => {
        if (processedUrl) {
            const a = document.createElement('a')
            a.href = processedUrl
            a.download = `removed_bg_${file?.name || 'image'}.png`
            document.body.appendChild(a)
            a.click()
            a.remove()
        }
    }

    return (
        <div className="container mx-auto p-6 max-w-5xl">
            <h1 className="text-3xl font-bold mb-8">AI Background Remover</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <Card>
                    <CardHeader>
                        <CardTitle>Upload Image</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center hover:bg-gray-50 transition-colors">
                            <Input
                                type="file"
                                accept="image/*"
                                className="hidden"
                                id="image-upload"
                                onChange={handleFileChange}
                            />
                            <label htmlFor="image-upload" className="cursor-pointer flex flex-col items-center">
                                <Upload className="h-10 w-10 text-gray-400 mb-2" />
                                <span className="text-sm text-gray-600 font-medium">Click to upload image</span>
                                <span className="text-xs text-gray-400 mt-1">JPG, PNG up to 5MB</span>
                            </label>
                        </div>

                        {previewUrl && (
                            <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden">
                                <img src={previewUrl} alt="Original" className="object-contain w-full h-full" />
                            </div>
                        )}

                        <Button
                            className="w-full"
                            onClick={handleRemoveBg}
                            disabled={!file || loading}
                            size="lg"
                        >
                            {loading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...
                                </>
                            ) : (
                                "Remove Background"
                            )}
                        </Button>
                    </CardContent>
                </Card>

                <Card className="bg-slate-50">
                    <CardHeader>
                        <CardTitle>Result</CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col items-center justify-center h-full min-h-[400px]">
                        {processedUrl ? (
                            <div className="space-y-6 w-full">
                                <div className="relative aspect-video bg-[url('https://ui.shadcn.com/placeholder.svg')] bg-repeat rounded-lg overflow-hidden border bg-white shadow-sm">
                                    {/* Checkerboard pattern for transparency */}
                                    <div className="absolute inset-0 opacity-20"
                                        style={{ backgroundImage: 'linear-gradient(45deg, #ccc 25%, transparent 25%), linear-gradient(-45deg, #ccc 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #ccc 75%), linear-gradient(-45deg, transparent 75%, #ccc 75%)', backgroundSize: '20px 20px', backgroundPosition: '0 0, 0 10px, 10px -10px, -10px 0px' }}>
                                    </div>
                                    <img src={processedUrl} alt="Processed" className="relative z-10 object-contain w-full h-full" />
                                </div>

                                <Button onClick={handleDownload} className="w-full" variant="outline">
                                    <Download className="mr-2 h-4 w-4" /> Download PNG
                                </Button>
                            </div>
                        ) : (
                            <div className="text-center text-gray-400">
                                <ImageIcon className="h-12 w-12 mx-auto mb-3 opacity-20" />
                                <p>Processed image will appear here</p>
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
