import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

export default function SectionHeader({
  eyebrow,
  title,
  description,
  action,
  className = '',
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between', className)}>
      <div className="max-w-3xl space-y-3">
        {eyebrow && (
          <p className="inline-flex rounded-full border-2 border-slate-950 bg-blue-100 px-3 py-1 font-mono text-xs font-bold uppercase tracking-[0.18em] text-slate-950 shadow-[3px_3px_0_rgba(17,24,39,0.18)]">
            {eyebrow}
          </p>
        )}
        <div className="space-y-3">
          <h1 className="font-display text-3xl font-normal leading-tight text-slate-950 sm:text-4xl">{title}</h1>
          {description && <p className="text-base leading-7 text-slate-600">{description}</p>}
        </div>
      </div>
      {action && <div className="shrink-0">{action}</div>}
    </div>
  );
}
