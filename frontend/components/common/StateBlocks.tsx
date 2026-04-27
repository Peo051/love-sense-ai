import { AlertTriangle, HeartHandshake, Loader2 } from 'lucide-react';
import type { ReactNode } from 'react';

import Card from '@/components/common/Card';
import { cn } from '@/lib/utils';

export function EmptyState({
  title,
  description,
  action,
  className = '',
}: {
  title: string;
  description: string;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <Card className={cn('border-dashed bg-rose-50/40', className)}>
      <div className="flex min-h-60 flex-col items-center justify-center px-4 py-10 text-center">
        <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-rose-600 shadow-sm">
          <HeartHandshake className="h-6 w-6" aria-hidden="true" />
        </div>
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">{description}</p>
        {action && <div className="mt-5">{action}</div>}
      </div>
    </Card>
  );
}

export function LoadingState({ title, description }: { title: string; description: string }) {
  return (
    <Card>
      <div role="status" aria-live="polite" className="flex min-h-60 flex-col items-center justify-center px-4 py-10 text-center">
        <Loader2 className="mb-4 h-8 w-8 animate-spin text-rose-600" aria-hidden="true" />
        <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
        <p className="mt-2 max-w-md text-sm leading-6 text-slate-600">{description}</p>
      </div>
    </Card>
  );
}

export function ErrorState({ title, description }: { title: string; description: string }) {
  return (
    <Card className="border-red-100 bg-red-50/80">
      <div role="alert" className="flex gap-3 text-red-800">
        <AlertTriangle className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
        <div>
          <h2 className="font-semibold">{title}</h2>
          <p className="mt-1 text-sm leading-6">{description}</p>
        </div>
      </div>
    </Card>
  );
}
