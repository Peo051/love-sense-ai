import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

type BadgeTone = 'rose' | 'teal' | 'amber' | 'slate';

const toneStyles: Record<BadgeTone, string> = {
  rose: 'border-slate-950 bg-rose-100 text-slate-950 shadow-[3px_3px_0_rgba(17,24,39,0.18)]',
  teal: 'border-slate-950 bg-emerald-100 text-slate-950 shadow-[3px_3px_0_rgba(17,24,39,0.18)]',
  amber: 'border-slate-950 bg-amber-100 text-slate-950 shadow-[3px_3px_0_rgba(17,24,39,0.18)]',
  slate: 'border-slate-950 bg-white text-slate-950 shadow-[3px_3px_0_rgba(17,24,39,0.18)]',
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
        'inline-flex items-center gap-1.5 rounded-full border-2 px-3 py-1 font-mono text-[0.68rem] font-bold uppercase tracking-[0.16em] backdrop-blur',
        toneStyles[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
