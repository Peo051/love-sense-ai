import type { Metadata } from 'next';
import { Inter, JetBrains_Mono, Limelight } from 'next/font/google';

import Footer from '@/components/common/Footer';
import Navbar from '@/components/common/Navbar';
import { cn } from '@/lib/utils';
import '../styles/globals.css';

const inter = Inter({
  subsets: ['latin', 'vietnamese'],
  variable: '--font-body',
  display: 'swap',
});

const limelight = Limelight({
  subsets: ['latin'],
  weight: '400',
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
    <html lang="vi" className={cn(inter.variable, limelight.variable, jetBrainsMono.variable)}>
      <body>
        <Navbar />
        <main className="min-h-screen">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
