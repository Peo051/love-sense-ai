'use client';

import { FormEvent, useState } from 'react';
import { KeyRound, LogIn, ShieldCheck, UserPlus } from 'lucide-react';
import Link from 'next/link';

import { ErrorAlert, SuccessAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import { clearAuthToken, loginUser, registerUser } from '@/lib/api';
import { inputClassName } from '@/lib/ui';
import { cn } from '@/lib/utils';

const privacyNotes = [
  'Profile, history và consent được tách theo tài khoản.',
  'Không lưu nội dung chat nếu bạn chưa đồng ý.',
  'Bạn có thể xóa dữ liệu trong trang Riêng tư.',
];

export default function AuthPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoginMode, setIsLoginMode] = useState(true);
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatusMessage('');
    setErrorMessage('');
    setIsSubmitting(true);

    try {
      if (!isLoginMode) {
        await registerUser(email, password);
      }
      await loginUser(email, password);
      setStatusMessage('Đã đăng nhập. Hồ sơ, lịch sử và cài đặt riêng tư sẽ gắn với tài khoản này.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xử lý tài khoản.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLogout = () => {
    clearAuthToken();
    setStatusMessage('Đã đăng xuất khỏi trình duyệt này.');
    setErrorMessage('');
  };

  return (
    <PageShell size="normal" className="pb-12">
      <div className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr] lg:items-start">
        <section className="overflow-hidden rounded-[2rem] border border-rose-200 bg-white shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <div className="bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.16),transparent_26rem),linear-gradient(135deg,#fff1f2,#ffffff,#fff8f1)] p-6 sm:p-8">
            <Badge tone="teal">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
              Dữ liệu theo từng tài khoản
            </Badge>
            <div className="mt-6 space-y-3">
              <h1 className="font-display text-4xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-5xl">
                Đăng nhập để quản lý dữ liệu của riêng bạn
              </h1>
              <p className="text-sm leading-6 text-slate-600">
                Tài khoản giúp CodeSense AI tách hồ sơ, lịch sử và consent theo từng người dùng. Ứng dụng không tự
                truy cập tin nhắn và không lưu chat nếu bạn chưa bật consent.
              </p>
            </div>
          </div>

          <div className="grid gap-3 p-6 sm:p-8">
            {privacyNotes.map((item) => (
              <div key={item} className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-rose-50 px-4 py-3 text-sm font-medium text-slate-700">
                <KeyRound className="h-4 w-4 shrink-0 text-rose-600" aria-hidden="true" />
                {item}
              </div>
            ))}
          </div>
        </section>

        <Card
          title={isLoginMode ? 'Đăng nhập' : 'Đăng ký tài khoản'}
          description={
            isLoginMode
              ? 'Nhập email và mật khẩu để tiếp tục phiên làm việc.'
              : 'Tạo tài khoản mới, sau đó hệ thống sẽ đăng nhập tự động.'
          }
        >
          <div className="mb-5 grid grid-cols-2 rounded-2xl border border-slate-200 bg-rose-50/60 p-1">
            {[
              { value: true, label: 'Đăng nhập' },
              { value: false, label: 'Đăng ký' },
            ].map((item) => (
              <button
                key={item.label}
                type="button"
                onClick={() => {
                  setIsLoginMode(item.value);
                  setStatusMessage('');
                  setErrorMessage('');
                }}
                className={cn(
                  'rounded-xl px-3 py-2 text-sm font-bold transition focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2',
                  isLoginMode === item.value ? 'bg-white text-rose-700 shadow-sm' : 'text-slate-600 hover:text-rose-700'
                )}
              >
                {item.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
            {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

            <div className="grid gap-4">
              <FieldLabel htmlFor="email" label="Email" hint="Dùng email bạn muốn gắn với hồ sơ và lịch sử phân tích.">
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
                  required
                  disabled={isSubmitting}
                  className={inputClassName}
                />
              </FieldLabel>

              <FieldLabel
                htmlFor="password"
                label="Mật khẩu"
                hint="Tối thiểu 6 ký tự. Không dùng mật khẩu đã chia sẻ ở nơi khác."
              >
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete={isLoginMode ? 'current-password' : 'new-password'}
                  required
                  minLength={6}
                  disabled={isSubmitting}
                  className={inputClassName}
                />
              </FieldLabel>
            </div>

            <Button type="submit" isLoading={isSubmitting} size="lg" className="w-full">
              {isLoginMode ? <LogIn className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
              {isSubmitting ? 'Đang xử lý' : isLoginMode ? 'Đăng nhập' : 'Đăng ký và đăng nhập'}
            </Button>

            <div className="flex flex-col gap-3 border-t border-rose-100 pt-4 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md text-left font-bold text-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 hover:text-rose-800"
              >
                Đăng xuất khỏi trình duyệt này
              </button>
              <Link
                href="/analyze"
                className="rounded-md font-bold text-slate-800 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 hover:text-rose-700"
              >
                Quay lại phân tích
              </Link>
            </div>
          </form>
        </Card>
      </div>
    </PageShell>
  );
}
