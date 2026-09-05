import type { Metadata } from 'next';
import { Be_Vietnam_Pro, JetBrains_Mono } from 'next/font/google';

import Footer from '@/components/common/Footer';
import Navbar from '@/components/common/Navbar';
import { cn } from '@/lib/utils';
import Providers from './providers';
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
  title: 'CodeSense AI - Adaptive Programming Tutor for Beginner C# OOP Students',
  description: 'Hệ thống gia sư lập trình thích ứng hỗ trợ sinh viên học lập trình hướng đối tượng C# OOP, phân tích code và gợi ý tư duy từng bước.',
  icons: {
    icon: [
      { url: '/logo.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: 'any' },
      { url: '/icon.png', type: 'image/png' },
    ],
    shortcut: '/favicon.ico',
    apple: '/apple-icon.png',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={cn(beVietnamPro.variable, beVietnamDisplay.variable, jetBrainsMono.variable)}>
      <body>
        <Providers>
          <Navbar />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
