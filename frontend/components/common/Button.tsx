import type { ButtonHTMLAttributes, ReactNode } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost';

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
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-5 py-2.5 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-offset-2';
  const variantStyles: Record<ButtonVariant, string> = {
    primary: 'bg-rose-600 text-white shadow-sm hover:bg-rose-700 focus:ring-rose-500',
    secondary: 'bg-amber-100 text-amber-950 hover:bg-amber-200 focus:ring-amber-400',
    ghost: 'bg-transparent text-slate-700 hover:bg-white/70 focus:ring-slate-300',
  };

  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={`${baseStyles} ${variantStyles[variant]} ${
        disabled || isLoading ? 'cursor-not-allowed opacity-60' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
