import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-rose-100 bg-white/80">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p>© 2026 Love Sense AI. Kết quả chỉ mang tính tham khảo, không thay thế giao tiếp trực tiếp.</p>
        <div className="flex flex-wrap gap-4">
          <Link href="/privacy" className="font-medium text-rose-700 hover:text-rose-800">
            Quyền riêng tư
          </Link>
          <Link href="/analyze" className="font-medium text-slate-700 hover:text-rose-700">
            Phân tích hội thoại
          </Link>
        </div>
      </div>
    </footer>
  );
}
