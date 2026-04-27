import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
  headerClassName?: string;
  bodyClassName?: string;
  variant?: 'default' | 'flat' | 'artistic' | 'dark';
}

export default function Card({
  children,
  title,
  description,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  variant = 'default',
}: CardProps) {
  const variantClassName = {
    default:
      'border border-slate-200 bg-white shadow-[0_18px_50px_rgba(15,23,42,0.06)] hover:shadow-[0_22px_60px_rgba(15,23,42,0.08)]',
    flat: 'border border-slate-200 bg-white shadow-none',
    artistic:
      'border-2 border-slate-900 bg-[linear-gradient(135deg,#ffffff_0%,#fff1f2_58%,#ccfbf1_100%)] shadow-[6px_6px_0_rgba(31,41,55,0.13)]',
    dark: 'border-2 border-slate-950 bg-slate-950 text-white shadow-[7px_7px_0_rgba(244,63,94,0.22)]',
  }[variant];

  return (
    <section
      className={cn(
        'rounded-[24px] p-5 backdrop-blur transition duration-200',
        variantClassName,
        className
      )}
    >
      {(title || description) && (
        <div className={cn('mb-5 space-y-1.5', headerClassName)}>
          {title && (
            <h2 className={cn('text-lg font-bold tracking-tight', variant === 'dark' ? 'text-white' : 'text-slate-950')}>
              {title}
            </h2>
          )}
          {description && (
            <p className={cn('text-sm leading-6', variant === 'dark' ? 'text-slate-300' : 'text-slate-600')}>
              {description}
            </p>
          )}
        </div>
      )}
      <div className={bodyClassName}>{children}</div>
    </section>
  );
}
