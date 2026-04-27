'use client';

import { LockKeyhole } from 'lucide-react';
import Link from 'next/link';

import { EmptyState, LoadingState } from '@/components/common/StateBlocks';

export default function AuthRequiredState({ title, description }: { title: string; description: string }) {
  return (
    <EmptyState
      title={title}
      description={description}
      action={
        <Link
          href="/login"
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border-2 border-rose-950 bg-rose-600 px-5 py-2.5 text-sm font-extrabold text-white shadow-[4px_4px_0_rgba(127,29,29,0.24)] transition hover:-translate-y-0.5 hover:bg-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2"
        >
          <LockKeyhole className="h-4 w-4" aria-hidden="true" />
          Đăng nhập
        </Link>
      }
    />
  );
}

export function AuthLoadingState() {
  return (
    <LoadingState
      title="Đang kiểm tra phiên đăng nhập"
      description="Love Sense AI đang kiểm tra Firebase ID Token trước khi tải dữ liệu cá nhân."
    />
  );
}
