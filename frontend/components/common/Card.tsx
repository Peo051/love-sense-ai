import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
}

export default function Card({
  children,
  title,
  description,
  className = '',
  headerClassName = '',
  bodyClassName = '',
}: CardProps) {
  return (
    <section
      className={cn(
        'rounded-2xl border border-rose-100/80 bg-white/95 p-5 shadow-[0_14px_45px_rgba(244,63,94,0.06)] ring-1 ring-white/70 backdrop-blur transition-shadow duration-200 hover:shadow-[0_18px_55px_rgba(244,63,94,0.08)]',
        className
      )}
    >
      {(title || description) && (
        <div className={cn('mb-5 space-y-1.5', headerClassName)}>
          {title && <h2 className="text-lg font-semibold text-slate-950">{title}</h2>}
          {description && <p className="text-sm leading-6 text-slate-600">{description}</p>}
        </div>
      )}
      <div className={bodyClassName}>{children}</div>
    </section>
  );
}
