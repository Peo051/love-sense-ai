import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  title?: string;
  description?: string;
  className?: string;
}

export default function Card({ children, title, description, className = '' }: CardProps) {
  return (
    <section className={`rounded-lg border border-rose-100 bg-white p-5 shadow-sm ${className}`}>
      {(title || description) && (
        <div className="mb-4 space-y-1">
          {title && <h2 className="text-lg font-semibold text-slate-950">{title}</h2>}
          {description && <p className="text-sm leading-6 text-slate-600">{description}</p>}
        </div>
      )}
      {children}
    </section>
  );
}
