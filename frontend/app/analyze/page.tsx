'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowRight, Code2 } from 'lucide-react';

import PageShell from '@/components/common/PageShell';

export default function AnalyzePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/tutor');
  }, [router]);

  return (
    <PageShell className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <div className="mx-auto max-w-md space-y-4 rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
          <Code2 className="h-7 w-7" />
        </div>
        <h1 className="text-xl font-bold text-slate-900">Đang chuyển hướng sang Gia sư lập trình...</h1>
        <p className="text-sm text-slate-600">
          Tính năng phân tích hội thoại cũ đã được chuyển đổi thành không gian hướng dẫn lập trình C# OOP.
        </p>
        <Link
          href="/tutor"
          className="inline-flex items-center gap-2 rounded-xl bg-rose-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-rose-700"
        >
          Đi tới CodeSense Tutor
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </PageShell>
  );
}
