import type { Metadata } from 'next';

import Footer from '@/components/common/Footer';
import Navbar from '@/components/common/Navbar';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: 'Love Emotion - Phân tích cảm xúc tình cảm',
  description: 'Ứng dụng web hỗ trợ phân tích sắc thái cảm xúc trong đoạn hội thoại tình cảm.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
