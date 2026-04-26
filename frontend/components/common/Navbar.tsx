import { HeartHandshake } from 'lucide-react';
import Link from 'next/link';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-rose-100 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="inline-flex items-center gap-2 text-lg font-bold text-slate-950">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-rose-600 text-white">
            <HeartHandshake className="h-5 w-5" aria-hidden="true" />
          </span>
          Love Emotion
        </Link>

        <div className="flex items-center gap-2 text-sm font-medium text-slate-700 sm:gap-5">
          <Link href="/analyze" className="rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700">
            Phân tích
          </Link>
          <Link href="/profile" className="rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700">
            Hồ sơ
          </Link>
          <Link href="/history" className="rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700">
            Lịch sử
          </Link>
          <Link href="/privacy" className="rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700">
            Riêng tư
          </Link>
          <Link href="/auth" className="rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700">
            Tài khoản
          </Link>
        </div>
      </nav>
    </header>
  );
}
