import type { Metadata } from 'next';
import { Be_Vietnam_Pro, JetBrains_Mono } from 'next/font/google';

import Footer from '@/components/common/Footer';
import Navbar from '@/components/common/Navbar';
import { cn } from '@/lib/utils';
import '../styles/globals.css';

const beVietnamPro = Be_Vietnam_Pro({
  subsets: ['latin', 'vietnamese'],
  weight: ['400', '500', '600', '700', '800'],
  variable: '--font-body',
  display: 'swap',
});

const beVietnamDisplay = Be_Vietnam_Pro({
  subsets: ['latin', 'vietnamese'],
  weight: ['700', '800'],
  variable: '--font-display',
  display: 'swap',
});

const jetBrainsMono = JetBrains_Mono({
  subsets: ['latin', 'vietnamese'],
  variable: '--font-mono',
  display: 'swap',
});

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
    <html lang="vi" className={cn(beVietnamPro.variable, beVietnamDisplay.variable, jetBrainsMono.variable)}>
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
