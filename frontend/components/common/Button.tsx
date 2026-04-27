import type { ButtonHTMLAttributes, ReactNode } from 'react';

import { cn } from '@/lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  isLoading?: boolean;
}

export default function Button({
  children,
  className = '',
  disabled = false,
  isLoading = false,
  type = 'button',
  variant = 'primary',
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantStyles: Record<ButtonVariant, string> = {
    primary: 'bg-rose-600 text-white shadow-sm shadow-rose-200 hover:bg-rose-700 focus:ring-rose-500',
    secondary: 'border border-rose-100 bg-white text-slate-800 shadow-sm hover:border-rose-200 hover:bg-rose-50 focus:ring-rose-300',
    danger: 'border border-red-200 bg-red-50 text-red-800 hover:bg-red-100 focus:ring-red-300',
    ghost: 'bg-transparent text-slate-700 hover:bg-rose-50 hover:text-rose-700 focus:ring-rose-300',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={cn(baseStyles, variantStyles[variant], disabled || isLoading ? 'cursor-not-allowed opacity-60' : '', className)}
      {...props}
    >
      {children}
    </button>
  );
}
