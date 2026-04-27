import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

type BadgeTone = 'rose' | 'teal' | 'amber' | 'slate';

const toneStyles: Record<BadgeTone, string> = {
  rose: 'border-rose-200 bg-rose-50 text-rose-700',
  teal: 'border-teal-200 bg-teal-50 text-teal-700',
  amber: 'border-amber-200 bg-amber-50 text-amber-800',
  slate: 'border-slate-200 bg-slate-50 text-slate-700',
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
        'inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold',
        toneStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
