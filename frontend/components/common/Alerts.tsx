import { AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import type { ReactNode } from 'react';

import { cn } from '@/lib/utils';

function AlertShell({
  children,
  className,
  role,
}: {
  children: ReactNode;
  className: string;
  role: 'alert' | 'status';
}) {
  return (
    <div role={role} className={cn('flex gap-3 rounded-2xl border px-4 py-3 text-sm leading-6', className)}>
      {children}
    </div>
  );
}

export function ErrorAlert({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <AlertShell role="alert" className={cn('border-red-200 bg-red-50 text-red-800', className)}>
      <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </AlertShell>
  );
}

export function SuccessAlert({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <AlertShell role="status" className={cn('border-teal-200 bg-teal-50 text-teal-800', className)}>
      <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </AlertShell>
  );
}

export function InfoAlert({ children, className = '' }: { children: ReactNode; className?: string }) {
  return (
    <AlertShell role="status" className={cn('border-rose-200 bg-rose-50 text-rose-800', className)}>
      <Info className="mt-0.5 h-5 w-5 shrink-0" aria-hidden="true" />
      <div>{children}</div>
    </AlertShell>
  );
}
