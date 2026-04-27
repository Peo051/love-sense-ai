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
    <PageShell size="normal">
      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-start">
        <section className="space-y-6 rounded-[2rem] border border-rose-100 bg-white p-6 shadow-sm sm:p-8">
          <Badge tone="rose">
            <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
            Dữ liệu theo từng tài khoản
          </Badge>
          <div className="space-y-3">
            <h1 className="text-3xl font-bold tracking-tight text-slate-950">Đăng nhập để lưu dữ liệu của riêng bạn</h1>
            <p className="text-sm leading-6 text-slate-600">
              Tài khoản giúp tách hồ sơ, lịch sử và consent theo từng người dùng. Love Sense AI không tự đọc tin nhắn
              và không lưu nội dung chat nếu bạn chưa đồng ý.
            </p>
          </div>
          <div className="grid gap-3">
            {['Profile/history/consent scoped theo user_id', 'Không lưu chat mặc định', 'Có thể xóa dữ liệu trong trang Riêng tư'].map(
              (item) => (
                <div key={item} className="flex items-center gap-3 rounded-2xl bg-rose-50 px-4 py-3 text-sm text-slate-700">
                  <KeyRound className="h-4 w-4 text-rose-600" aria-hidden="true" />
                  {item}
                </div>
              )
            )}
          </div>
        </section>

        <Card
          title={isLoginMode ? 'Đăng nhập' : 'Đăng ký tài khoản'}
          description={isLoginMode ? 'Nhập email và mật khẩu để tiếp tục.' : 'Tạo tài khoản mới, sau đó hệ thống sẽ đăng nhập tự động.'}
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
            {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

            <div className="grid gap-4">
              <FieldLabel htmlFor="email" label="Email">
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  autoComplete="email"
                  required
                  className="w-full rounded-2xl border border-rose-100 px-4 py-3 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
                />
              </FieldLabel>

              <FieldLabel htmlFor="password" label="Mật khẩu" hint="Tối thiểu 6 ký tự. Không dùng mật khẩu bạn đã chia sẻ ở nơi khác.">
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  autoComplete={isLoginMode ? 'current-password' : 'new-password'}
                  required
                  minLength={6}
                  className="w-full rounded-2xl border border-rose-100 px-4 py-3 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
                />
              </FieldLabel>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <Button type="submit" isLoading={isSubmitting}>
                {isLoginMode ? <LogIn className="h-4 w-4" /> : <UserPlus className="h-4 w-4" />}
                {isSubmitting ? 'Đang xử lý' : isLoginMode ? 'Đăng nhập' : 'Đăng ký và đăng nhập'}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setIsLoginMode((current) => !current)}>
                {isLoginMode ? 'Tạo tài khoản mới' : 'Đã có tài khoản'}
              </Button>
            </div>

            <div className="flex flex-col gap-3 border-t border-rose-100 pt-4 text-sm text-slate-600">
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-md text-left font-medium text-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2"
              >
                Đăng xuất khỏi trình duyệt này
              </button>
              <Link
                href="/analyze"
                className="rounded-md font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2"
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
