import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

export default function PageShell({
  children,
  className = '',
  size = 'wide',
}: {
  children: ReactNode;
  className?: string;
  size?: 'normal' | 'wide' | 'narrow';
}) {
  const maxWidth = {
    narrow: 'max-w-4xl',
    normal: 'max-w-6xl',
    wide: 'max-w-7xl',
  }[size];

  return <div className={cn('mx-auto w-full px-4 py-8 sm:px-6 lg:px-8', maxWidth, className)}>{children}</div>;
}
