import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-100 mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center">
          <p className="text-gray-600">
            © 2026 Love Emotion. All rights reserved.
          </p>
          
          <div className="flex gap-4">
            <Link href="/privacy" className="text-gray-600 hover:text-pink-600">
              Chính sách bảo mật
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
