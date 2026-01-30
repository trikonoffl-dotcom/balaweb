import Link from 'next/link'
import Image from 'next/image'
import { BackendStatus } from '../backend-status'

export function Header() {
    return (
        <header className="border-b bg-white">
            <div className="flex h-16 items-center px-6">
                <Link href="/dashboard" className="flex items-center gap-2 font-semibold">
                    <div className="relative w-32 h-10">
                        <Image
                            src="/trikon_logo.png"
                            alt="Trikon Logo"
                            fill
                            sizes="(max-width: 768px) 100vw, 128px"
                            className="object-contain object-left"
                            priority
                        />
                    </div>
                </Link>
                <div className="ml-auto flex items-center space-x-4">
                    <BackendStatus />
                </div>
            </div>
        </header>
    )
}
