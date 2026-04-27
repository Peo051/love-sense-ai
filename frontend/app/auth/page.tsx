'use client';

import { FormEvent, useState } from 'react';
import { LogIn, UserPlus } from 'lucide-react';
import Link from 'next/link';

import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
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
    <div className="mx-auto w-full max-w-xl px-4 py-10 sm:px-6 lg:px-8">
      <Card
        title={isLoginMode ? 'Đăng nhập' : 'Đăng ký tài khoản'}
        description="Tài khoản giúp tách dữ liệu hồ sơ, lịch sử và consent theo từng người dùng. Ứng dụng không đọc tin nhắn hay lưu nội dung chat nếu bạn chưa đồng ý."
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          {statusMessage && (
            <p role="status" className="rounded-md bg-teal-50 px-4 py-3 text-sm text-teal-800">
              {statusMessage}
            </p>
          )}
          {errorMessage && (
            <p role="alert" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </p>
          )}

          <label className="space-y-2 text-sm font-medium text-slate-800">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              autoComplete="email"
              required
              className="w-full rounded-md border border-rose-100 px-3 py-2 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
            />
          </label>

          <label className="space-y-2 text-sm font-medium text-slate-800">
            <span>Mật khẩu</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete={isLoginMode ? 'current-password' : 'new-password'}
              required
              minLength={6}
              className="w-full rounded-md border border-rose-100 px-3 py-2 text-sm outline-none focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
            />
          </label>

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
  );
}
