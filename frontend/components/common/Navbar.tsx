'use client';

import { HeartHandshake, Menu, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

import { cn } from '@/lib/utils';

const navItems = [
  { href: '/analyze', label: 'Phân tích' },
  { href: '/profile', label: 'Hồ sơ' },
  { href: '/history', label: 'Lịch sử' },
  { href: '/privacy', label: 'Riêng tư' },
  { href: '/auth', label: 'Tài khoản' },
];

export default function Navbar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="sticky top-0 z-30 border-b-2 border-slate-950 bg-white/92 shadow-[0_6px_0_rgba(17,24,39,0.08)] backdrop-blur-xl">
      <nav aria-label="Điều hướng chính" className="mx-auto max-w-7xl px-3 min-[390px]:px-4 sm:px-6 lg:px-8">
        <div className="flex min-h-16 items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex min-w-0 items-center gap-2 rounded-xl text-base font-black text-slate-950 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2"
            onClick={() => setIsOpen(false)}
          >
            <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border-2 border-slate-950 bg-gradient-to-br from-blue-500 to-violet-600 text-white shadow-[4px_4px_0_rgba(17,24,39,0.2)] sm:h-10 sm:w-10">
              <HeartHandshake className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="truncate">
              Love Sense <span className="text-blue-600">AI</span>
            </span>
          </Link>

          <div className="hidden items-center gap-1 rounded-2xl border-2 border-slate-950 bg-white p-1 font-mono text-xs font-bold uppercase tracking-[0.08em] text-slate-700 shadow-[4px_4px_0_rgba(17,24,39,0.12)] md:flex">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'rounded-xl px-3 py-2 transition focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2',
                    isActive
                      ? 'bg-blue-600 text-white shadow-[3px_3px_0_rgba(17,24,39,0.22)]'
                      : 'hover:bg-blue-50 hover:text-blue-700'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>

          <button
            type="button"
            className="inline-flex h-11 w-11 items-center justify-center rounded-xl border-2 border-slate-950 bg-white text-slate-700 shadow-[4px_4px_0_rgba(17,24,39,0.16)] focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2 md:hidden"
            aria-label={isOpen ? 'Đóng menu' : 'Mở menu'}
            aria-expanded={isOpen}
            onClick={() => setIsOpen((current) => !current)}
          >
            {isOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </button>
        </div>

        {isOpen && (
          <div className="grid gap-2 border-t-2 border-slate-950 py-3 md:hidden">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'rounded-xl border-2 px-3 py-3 text-sm font-bold transition focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2',
                    isActive
                      ? 'border-slate-950 bg-blue-600 text-white shadow-[4px_4px_0_rgba(17,24,39,0.16)]'
                      : 'border-transparent text-slate-700 hover:border-slate-950 hover:bg-blue-50 hover:text-blue-700'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
        )}
      </nav>
    </header>
  );
}
