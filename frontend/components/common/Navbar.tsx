'use client';

import { Code2, LogIn, LogOut, Menu, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState } from 'react';

import { useAuth } from '@/contexts/AuthContext';
import { logout } from '@/lib/auth';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/analyze', label: 'Phân tích' },
  { href: '/profile', label: 'Hồ sơ' },
  { href: '/history', label: 'Lịch sử' },
  { href: '/privacy', label: 'Riêng tư' },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const displayName = user?.displayName || user?.email || 'Tài khoản Google';

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
    router.push('/');
  };

  return (
    <header className="sticky top-0 z-30 border-b border-rose-100 bg-white/92 shadow-[0_10px_30px_rgba(15,23,42,0.06)] backdrop-blur-xl">
      <nav aria-label="Điều hướng chính" className="mx-auto max-w-7xl px-3 min-[390px]:px-4 sm:px-6 lg:px-8">
        <div className="flex min-h-16 items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex min-w-0 items-center gap-2 rounded-xl text-base font-extrabold text-slate-950 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
            onClick={() => setIsOpen(false)}
          >
            <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-rose-200 bg-gradient-to-br from-rose-500 to-rose-700 text-white shadow-[4px_4px_0_rgba(127,29,29,0.16)] sm:h-10 sm:w-10">
              <Code2 className="h-5 w-5" aria-hidden="true" />
            </span>
            <span className="truncate">
              CodeSense <span className="text-rose-600">AI</span>
            </span>
          </Link>

          <div className="hidden items-center gap-3 md:flex">
            <div className="flex items-center gap-1 rounded-2xl border border-rose-100 bg-white/90 p-1 font-mono text-xs font-bold uppercase tracking-[0.08em] text-slate-700 shadow-sm shadow-rose-100/70">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      'rounded-xl px-3 py-2 transition focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2',
                      isActive
                        ? 'bg-rose-600 text-white shadow-sm shadow-rose-200'
                        : 'hover:bg-rose-50 hover:text-rose-700'
                    )}
                    aria-current={isActive ? 'page' : undefined}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>

            {!loading && isAuthenticated ? (
              <div className="flex items-center gap-2 rounded-2xl border border-rose-100 bg-white/90 px-2 py-1 shadow-sm shadow-rose-100/70">
                {user?.photoURL ? (
                  <img
                    src={user.photoURL}
                    alt=""
                    referrerPolicy="no-referrer"
                    className="h-8 w-8 rounded-full border border-rose-100"
                  />
                ) : (
                  <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-rose-100 text-xs font-extrabold text-rose-700">
                    {(displayName[0] ?? 'U').toUpperCase()}
                  </span>
                )}
                <span className="max-w-36 truncate text-sm font-bold text-slate-800">{displayName}</span>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-slate-600 transition hover:bg-rose-50 hover:text-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
                  aria-label="Đăng xuất"
                >
                  <LogOut className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="inline-flex min-h-10 items-center justify-center gap-2 rounded-xl border-2 border-rose-950 bg-rose-600 px-4 py-2 text-sm font-extrabold text-white shadow-[4px_4px_0_rgba(127,29,29,0.22)] transition hover:-translate-y-0.5 hover:bg-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
              >
                <LogIn className="h-4 w-4" aria-hidden="true" />
                Đăng nhập
              </Link>
            )}
          </div>

          <button
            type="button"
            className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-rose-200 bg-white text-slate-700 shadow-sm shadow-rose-100 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 md:hidden"
            aria-label={isOpen ? 'Đóng menu' : 'Mở menu'}
            aria-expanded={isOpen}
            onClick={() => setIsOpen((current) => !current)}
          >
            {isOpen ? <X className="h-5 w-5" aria-hidden="true" /> : <Menu className="h-5 w-5" aria-hidden="true" />}
          </button>
        </div>

        {isOpen && (
          <div className="grid gap-2 border-t border-rose-100 py-3 md:hidden">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setIsOpen(false)}
                  className={cn(
                    'rounded-xl border px-3 py-3 text-sm font-bold transition focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2',
                    isActive
                      ? 'border-rose-600 bg-rose-600 text-white shadow-sm shadow-rose-200'
                      : 'border-transparent text-slate-700 hover:border-rose-200 hover:bg-rose-50 hover:text-rose-700'
                  )}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.label}
                </Link>
              );
            })}
            {!loading && isAuthenticated ? (
              <div className="rounded-2xl border border-rose-100 bg-white p-3">
                <p className="truncate text-sm font-bold text-slate-900">{displayName}</p>
                <p className="mt-1 truncate text-xs text-slate-500">{user?.email ?? 'Đã đăng nhập'}</p>
                <button
                  type="button"
                  onClick={handleLogout}
                  className="mt-3 inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2 text-sm font-bold text-slate-800 transition hover:bg-rose-50 hover:text-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
                >
                  <LogOut className="h-4 w-4" aria-hidden="true" />
                  Đăng xuất
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                onClick={() => setIsOpen(false)}
                className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border-2 border-rose-950 bg-rose-600 px-4 py-2 text-sm font-extrabold text-white shadow-[4px_4px_0_rgba(127,29,29,0.22)] transition focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
              >
                <LogIn className="h-4 w-4" aria-hidden="true" />
                Đăng nhập
              </Link>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}
