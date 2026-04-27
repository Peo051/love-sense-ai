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
    <header className="sticky top-0 z-30 border-b border-rose-100/80 bg-white/90 backdrop-blur-xl">
      <nav aria-label="Điều hướng chính" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex min-h-16 items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-xl text-base font-bold text-slate-950 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2"
            onClick={() => setIsOpen(false)}
          >
            <span className="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-rose-500 to-rose-700 text-white shadow-sm shadow-rose-200">
              <HeartHandshake className="h-5 w-5" aria-hidden="true" />
            </span>
            <span>
              Love Sense <span className="text-rose-600">AI</span>
            </span>
          </Link>

          <div className="hidden items-center gap-1 rounded-2xl border border-rose-100 bg-white/85 p-1 text-sm font-medium text-slate-700 shadow-sm shadow-rose-100/50 md:flex">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'rounded-xl px-3 py-2 transition focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2',
                    isActive
                      ? 'bg-rose-600 text-white shadow-sm shadow-rose-200/70'
                      : 'hover:bg-rose-50 hover:text-rose-700'
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
            className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-rose-100 bg-white text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 md:hidden"
            aria-label={isOpen ? 'Đóng menu' : 'Mở menu'}
            aria-expanded={isOpen}
            onClick={() => setIsOpen((current) => !current)}
          >
            {isOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </button>
        </div>

        {isOpen && (
          <div className="grid gap-1 border-t border-rose-100 py-3 md:hidden">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'rounded-xl px-3 py-3 text-sm font-semibold focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2',
                    isActive ? 'bg-rose-600 text-white' : 'text-slate-700 hover:bg-rose-50 hover:text-rose-700'
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
