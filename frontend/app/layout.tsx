import type { Metadata } from 'next';

import Footer from '@/components/common/Footer';
import Navbar from '@/components/common/Navbar';
import '../styles/globals.css';

export const metadata: Metadata = {
  title: 'Love Sense AI - Phân tích sắc thái hội thoại',
  description: 'Ứng dụng hỗ trợ phân tích sắc thái hội thoại và gợi ý phản hồi nhẹ nhàng, ưu tiên quyền riêng tư.',
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
