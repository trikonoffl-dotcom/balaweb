'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableFooter } from "@/components/ui/table"
import { IconCalculator, IconTrash, IconFileSpreadsheet, IconTrendingUp } from '@tabler/icons-react'

interface IncentiveRow {
    id: string
    grenkeValue: number
    incentivePercentage: number
    incentiveAmountUSD: number
    conversionRate: number
    incentiveAmountINR: number
}

export default function HRPage() {
    const [grenkeValue, setGrenkeValue] = useState('')
    const [incentivePercentage, setIncentivePercentage] = useState('')
    const [conversionRate, setConversionRate] = useState('83.00')
    const [additionalRupees, setAdditionalRupees] = useState('')
    const [rows, setRows] = useState<IncentiveRow[]>([])

    useEffect(() => {
        const savedRate = localStorage.getItem('conversionRate')
        if (savedRate) setConversionRate(savedRate)
    }, [])

    const handleRateChange = (val: string) => {
        setConversionRate(val); localStorage.setItem('conversionRate', val)
    }

    const calculateIncentive = () => {
        const gValue = parseFloat(grenkeValue.replace(/[^0-9.]/g, '')) || 0
        const iPercent = parseFloat(incentivePercentage.replace(/[^0-9.]/g, '')) || 0
        const rate = parseFloat(conversionRate.replace(/[^0-9.]/g, '')) || 1
        const addINR = parseFloat(additionalRupees.replace(/[^0-9.]/g, '')) || 0
        const amountUSD = iPercent > 0 ? gValue * (iPercent / 100) : gValue
        const amountINR = Math.round(amountUSD * rate) + addINR
        setRows([...rows, {
            id: Date.now().toString(),
            grenkeValue: gValue, incentivePercentage: iPercent,
            incentiveAmountUSD: amountUSD, conversionRate: rate,
            incentiveAmountINR: amountINR
        }])
        setGrenkeValue(''); setIncentivePercentage(''); setAdditionalRupees('')
    }

    const removeRow = (id: string) => setRows(rows.filter(row => row.id !== id))
    const clearTable = () => { if (confirm("Clear all data?")) setRows([]) }
    const totalIncentive = rows.reduce((sum, row) => sum + row.incentiveAmountINR, 0)

    return (
        <div className="p-4 max-w-[1400px] mx-auto space-y-4">
            <div className="flex items-center justify-between bg-white p-3 rounded-lg shadow-sm border border-slate-200">
                <div className="flex items-center gap-2">
                    <IconTrendingUp className="h-5 w-5 text-green-600" />
                    <h1 className="text-xl font-bold text-slate-800 tracking-tight">Incentive Calculator</h1>
                </div>
                <div className="flex items-center gap-4">
                    <div className="text-right">
                        <p className="text-[10px] text-slate-400 font-bold uppercase">Total Payout</p>
                        <p className="text-xl font-black text-green-600 font-mono leading-none">₹{totalIncentive.toLocaleString()}</p>
                    </div>
                    <Button onClick={clearTable} variant="outline" size="sm" className="text-red-500 border-red-100 hover:bg-red-50 h-8">
                        <IconTrash className="h-3.5 w-3.5 mr-1" /> Clear
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-end bg-slate-50 p-4 rounded-xl border border-dashed border-slate-300">
                <div className="space-y-1">
                    <Label className="text-[10px] uppercase font-bold text-slate-500">Grenke ($)</Label>
                    <Input placeholder="5000" value={grenkeValue} onChange={e => setGrenkeValue(e.target.value)} className="h-9 bg-white" />
                </div>
                <div className="space-y-1">
                    <Label className="text-[10px] uppercase font-bold text-slate-500">Incentive (%)</Label>
                    <Input placeholder="10" value={incentivePercentage} onChange={e => setIncentivePercentage(e.target.value)} className="h-9 bg-white" />
                </div>
                <div className="space-y-1">
                    <Label className="text-[10px] uppercase font-bold text-slate-500">Rate (₹/$)</Label>
                    <Input value={conversionRate} onChange={e => handleRateChange(e.target.value)} className="h-9 bg-white font-bold text-blue-600" />
                </div>
                <div className="space-y-1">
                    <Label className="text-[10px] uppercase font-bold text-slate-500">Extra (₹)</Label>
                    <Input placeholder="0" value={additionalRupees} onChange={e => setAdditionalRupees(e.target.value)} className="h-9 bg-white" />
                </div>
                <Button className="w-full bg-green-600 hover:bg-green-700 h-9 font-bold" onClick={calculateIncentive}>
                    <IconCalculator className="mr-2 h-4 w-4" /> Add to Summary
                </Button>
            </div>

            <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
                <Table>
                    <TableHeader className="bg-slate-50/50">
                        <TableRow>
                            <TableHead className="text-[10px] h-8 py-0">Grenke ($)</TableHead>
                            <TableHead className="text-[10px] h-8 py-0">Inc %</TableHead>
                            <TableHead className="text-[10px] h-8 py-0">Inc ($)</TableHead>
                            <TableHead className="text-[10px] h-8 py-0">Rate</TableHead>
                            <TableHead className="text-[10px] h-8 py-0 text-right">Total (₹)</TableHead>
                            <TableHead className="w-10 h-8 py-0"></TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {rows.map(row => (
                            <TableRow key={row.id} className="h-10 hover:bg-slate-50/30">
                                <TableCell className="py-1 font-mono text-xs">${row.grenkeValue}</TableCell>
                                <TableCell className="py-1 font-mono text-xs">{row.incentivePercentage}%</TableCell>
                                <TableCell className="py-1 font-mono text-xs text-slate-500">${row.incentiveAmountUSD.toFixed(1)}</TableCell>
                                <TableCell className="py-1 font-mono text-xs text-slate-500">{row.conversionRate}</TableCell>
                                <TableCell className="py-1 font-black text-right text-xs">₹{row.incentiveAmountINR.toLocaleString()}</TableCell>
                                <TableCell className="py-1">
                                    <button onClick={() => removeRow(row.id)} className="text-slate-300 hover:text-red-500">
                                        <IconTrash className="h-3.5 w-3.5" />
                                    </button>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    )
}
