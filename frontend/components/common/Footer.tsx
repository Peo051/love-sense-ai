import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="mt-16 border-t border-rose-100 bg-white/85">
      <div className="mx-auto grid max-w-7xl gap-4 px-4 py-7 text-sm text-slate-600 sm:px-6 lg:grid-cols-[1fr_auto] lg:items-center lg:px-8">
        <div>
          <p className="font-semibold text-slate-950">Love Sense AI</p>
          <p className="mt-1 leading-6">
            Kết quả chỉ mang tính tham khảo, không thay thế giao tiếp trực tiếp và không lưu chat nếu bạn chưa đồng ý.
          </p>
        </div>
        <div className="flex flex-wrap gap-4">
          <Link
            href="/privacy"
            className="rounded-md font-medium text-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 hover:text-rose-800"
          >
            Quyền riêng tư
          </Link>
          <Link
            href="/analyze"
            className="rounded-md font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 hover:text-rose-700"
          >
            Phân tích hội thoại
          </Link>
        </div>
      </div>
    </footer>
  );
}
