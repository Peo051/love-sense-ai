import { HeartHandshake } from 'lucide-react';
import Link from 'next/link';

const navLinkClass =
  'rounded-md px-3 py-2 hover:bg-rose-50 hover:text-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2';

export default function Navbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-rose-100 bg-white/90 backdrop-blur">
      <nav
        aria-label="Điều hướng chính"
        className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8"
      >
        <Link
          href="/"
          className="inline-flex items-center gap-2 self-start rounded-md text-lg font-bold text-slate-950 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2"
        >
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-md bg-rose-600 text-white">
            <HeartHandshake className="h-5 w-5" aria-hidden="true" />
          </span>
          Love Emotion
        </Link>

        <div className="flex flex-wrap items-center gap-1 text-sm font-medium text-slate-700 sm:gap-2 lg:gap-5">
          <Link href="/analyze" className={navLinkClass}>
            Phân tích
          </Link>
          <Link href="/profile" className={navLinkClass}>
            Hồ sơ
          </Link>
          <Link href="/history" className={navLinkClass}>
            Lịch sử
          </Link>
          <Link href="/privacy" className={navLinkClass}>
            Riêng tư
          </Link>
          <Link href="/auth" className={navLinkClass}>
            Tài khoản
          </Link>
        </div>
      </nav>
    </header>
  );
}
