import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

type BadgeTone = 'rose' | 'teal' | 'amber' | 'slate';

const toneStyles: Record<BadgeTone, string> = {
  rose: 'border-rose-200 bg-rose-50 text-rose-800 shadow-rose-100/80',
  teal: 'border-teal-200 bg-teal-50 text-teal-800 shadow-teal-100/80',
  amber: 'border-amber-200 bg-amber-50 text-amber-900 shadow-amber-100/80',
  slate: 'border-slate-200 bg-white text-slate-700 shadow-slate-100/80',
};

export default function Badge({
  children,
  tone = 'rose',
  className = '',
}: {
  children: ReactNode;
  tone?: BadgeTone;
  className?: string;
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-[0.68rem] font-bold uppercase tracking-[0.14em] shadow-sm backdrop-blur',
        toneStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
