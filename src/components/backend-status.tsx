"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { getApiUrl } from '@/lib/api'

export function BackendStatus() {
    const [status, setStatus] = useState<'idle' | 'checking' | 'connected' | 'error'>('idle')
    const [latency, setLatency] = useState<number | null>(null)

    const checkHealth = async () => {
        setStatus('checking')
        const start = Date.now()
        try {
            const res = await fetch(getApiUrl('/health'))
            if (res.ok) {
                setStatus('connected')
                setLatency(Date.now() - start)
            } else {
                setStatus('error')
            }
        } catch (error) {
            console.error("Backend health check failed:", error)
            setStatus('error')
        }
    }

    // Checking on mount is optional, but user asked for a button. 
    // We can do both: auto-check once, but allow manual re-check.
    useEffect(() => {
        checkHealth()
    }, [])

    return (
        <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm">
                <span className={`h-2.5 w-2.5 rounded-full ${status === 'connected' ? 'bg-green-500' :
                        status === 'error' ? 'bg-red-500' :
                            status === 'checking' ? 'bg-yellow-500 animate-pulse' : 'bg-gray-300'
                    }`} />
                <span className={status === 'error' ? 'text-red-600 font-medium' : 'text-gray-600'}>
                    {status === 'idle' && 'Backend Idle'}
                    {status === 'checking' && 'Requesting Access...'}
                    {status === 'connected' && `Engine Online (${latency}ms)`}
                    {status === 'error' && 'Engine Offline'}
                </span>
            </div>

            {status !== 'connected' && (
                <Button
                    variant={status === 'error' ? "destructive" : "outline"}
                    size="sm"
                    onClick={checkHealth}
                    disabled={status === 'checking'}
                >
                    {status === 'checking' ? 'Connecting...' : 'Start Engine'}
                </Button>
            )}
        </div>
    )
}
