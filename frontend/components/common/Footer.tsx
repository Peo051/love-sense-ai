import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-rose-100 bg-white/90">
      <div className="mx-auto grid max-w-7xl gap-4 px-4 py-7 text-sm text-slate-600 sm:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
        <div>
          <p className="font-display text-xl font-extrabold tracking-tight text-slate-950">CodeSense AI</p>
          <p className="mt-1 leading-6">
            Adaptive Programming Tutor for Beginner C# OOP Students. Hỗ trợ tư duy lập trình và hướng dẫn giải quyết bài toán từng bước.
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link
            href="/privacy"
            className="rounded-md font-bold text-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 hover:text-rose-800"
          >
            Quyền riêng tư
          </Link>
          <Link
            href="/analyze"
            className="rounded-md font-bold text-slate-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 hover:text-rose-700"
          >
            Phân tích hội thoại
          </Link>
        </div>
      </div>
    </footer>
  );
}
