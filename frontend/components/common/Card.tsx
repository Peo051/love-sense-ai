import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  headerClassName?: string;
}

export default function Card({ children, title, description, className = '', headerClassName = '' }: CardProps) {
  return (
    <section className={cn('rounded-2xl border border-rose-100/80 bg-white/95 p-5 shadow-sm shadow-rose-100/50', className)}>
      {(title || description) && (
        <div className={cn('mb-5 space-y-1.5', headerClassName)}>
          {title && <h2 className="text-lg font-semibold text-slate-950">{title}</h2>}
          {description && <p className="text-sm leading-6 text-slate-600">{description}</p>}
        </div>
      )}
      {children}
    </section>
  );
}
