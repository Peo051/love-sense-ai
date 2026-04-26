import Link from 'next/link';

export default function Navbar() {
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-2xl font-bold text-pink-600">
            Love Emotion
          </Link>
          
          <div className="flex gap-6">
            <Link href="/analyze" className="hover:text-pink-600">
              Phân tích
            </Link>
            <Link href="/history" className="hover:text-pink-600">
              Lịch sử
            </Link>
            <Link href="/profile" className="hover:text-pink-600">
              Hồ sơ
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
