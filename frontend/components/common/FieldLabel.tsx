import type { ReactNode } from 'react';

export default function FieldLabel({
  htmlFor,
  label,
  hint,
  children,
}: {
  htmlFor?: string;
  label: string;
  hint?: string;
  children: ReactNode;
}) {
  if (!htmlFor) {
    return (
      <label className="block space-y-2">
        <span className="block text-sm font-semibold text-slate-950">{label}</span>
        {children}
        {hint && <span className="block text-xs leading-5 text-slate-500">{hint}</span>}
      </label>
    );
  }

  return (
    <div className="space-y-2">
      <label htmlFor={htmlFor} className="block text-sm font-semibold text-slate-950">
        {label}
      </label>
      {children}
      {hint && <p className="text-xs leading-5 text-slate-500">{hint}</p>}
    </div>
  );
}
