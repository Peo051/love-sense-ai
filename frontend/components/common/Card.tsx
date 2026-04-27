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
      'border-2 border-slate-900 bg-white shadow-[6px_6px_0_rgba(17,24,39,0.14)] hover:shadow-[8px_8px_0_rgba(17,24,39,0.18)]',
    flat: 'border-2 border-slate-900/70 bg-white shadow-none',
    artistic:
      'border-2 border-slate-900 bg-[linear-gradient(135deg,#ffffff_0%,#eff6ff_58%,#ede9fe_100%)] shadow-[8px_8px_0_rgba(17,24,39,0.18)]',
    dark: 'border-2 border-slate-950 bg-slate-950 text-white shadow-[8px_8px_0_rgba(59,130,246,0.34)]',
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
            <h2 className={cn('text-lg font-black tracking-tight', variant === 'dark' ? 'text-white' : 'text-slate-950')}>
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
