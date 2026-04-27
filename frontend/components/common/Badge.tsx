import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

type BadgeTone = 'rose' | 'teal' | 'amber' | 'slate';

const toneStyles: Record<BadgeTone, string> = {
  rose: 'border-rose-200/80 bg-rose-50/90 text-rose-700 shadow-rose-100/70',
  teal: 'border-teal-200/80 bg-teal-50/90 text-teal-700 shadow-teal-100/70',
  amber: 'border-amber-200/80 bg-amber-50/90 text-amber-800 shadow-amber-100/70',
  slate: 'border-slate-200/80 bg-white/80 text-slate-700 shadow-slate-100/70',
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
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold shadow-sm backdrop-blur',
        toneStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
