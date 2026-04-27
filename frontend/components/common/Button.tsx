import type { ButtonHTMLAttributes, ReactNode } from 'react';

import { cn } from '@/lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

export default function Button({
  children,
  className = '',
  disabled = false,
  isLoading = false,
  size = 'md',
  type = 'button',
  variant = 'primary',
  ...props
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 rounded-xl border-2 font-semibold transition duration-200 focus:outline-none focus-visible:ring-4 focus-visible:ring-offset-2 active:translate-y-0 disabled:shadow-none';
  const sizeStyles: Record<ButtonSize, string> = {
    sm: 'min-h-11 px-3 py-2 text-xs',
    md: 'min-h-11 px-5 py-2.5 text-sm',
    lg: 'min-h-12 px-6 py-3 text-base',
  };
  const variantStyles: Record<ButtonVariant, string> = {
    primary:
      'border-slate-950 bg-blue-600 text-white shadow-[5px_5px_0_#111827] hover:-translate-y-0.5 hover:bg-violet-600 focus-visible:ring-blue-200',
    secondary:
      'border-slate-950 bg-white text-slate-950 shadow-[4px_4px_0_rgba(17,24,39,0.18)] hover:-translate-y-0.5 hover:bg-blue-50 focus-visible:ring-blue-200',
    danger:
      'border-red-950 bg-red-600 text-white shadow-[4px_4px_0_rgba(127,29,29,0.38)] hover:-translate-y-0.5 hover:bg-red-700 focus-visible:ring-red-200',
    ghost: 'border-transparent bg-transparent text-slate-800 hover:bg-blue-50 hover:text-blue-700 focus-visible:ring-blue-200',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={cn(
        baseStyles,
        sizeStyles[size],
        variantStyles[variant],
        disabled || isLoading ? 'cursor-not-allowed opacity-60 hover:translate-y-0' : '',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
