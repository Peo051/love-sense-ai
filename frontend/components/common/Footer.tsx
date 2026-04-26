import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-14 border-t border-rose-100 bg-white">
      <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
        <p>© 2026 Love Emotion. Kết quả chỉ mang tính tham khảo.</p>
        <Link href="/privacy" className="font-medium text-rose-700 hover:text-rose-800">
          Chính sách riêng tư
        </Link>
      </div>
    </footer>
  );
}
