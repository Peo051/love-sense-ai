'use client';

import { useEffect, useState } from 'react';
import { ArrowRight, ShieldCheck } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { ErrorAlert, InfoAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import PageShell from '@/components/common/PageShell';
import { useAuth } from '@/contexts/AuthContext';
import { loginWithGoogle } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, loading } = useAuth();
  const [errorMessage, setErrorMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace('/analyze');
    }
  }, [isAuthenticated, loading, router]);

  const handleGoogleLogin = async () => {
    setErrorMessage('');
    setIsSubmitting(true);

    try {
      await loginWithGoogle();
      router.replace('/analyze');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể đăng nhập bằng Google.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <PageShell size="normal" className="pb-12">
      <div className="mx-auto grid max-w-5xl gap-6 lg:grid-cols-[0.95fr_1.05fr] lg:items-center">
        <section className="overflow-hidden rounded-[2rem] border border-rose-200 bg-white shadow-[0_18px_50px_rgba(15,23,42,0.08)]">
          <div className="bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.16),transparent_26rem),linear-gradient(135deg,#fff1f2,#ffffff,#fff8f1)] p-6 sm:p-8">
            <Badge tone="teal">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
              Google Login
            </Badge>
            <h1 className="mt-6 font-display text-4xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-5xl">
              Đăng nhập để lưu hồ sơ và lịch sử theo tài khoản
            </h1>
            <p className="mt-4 text-sm leading-6 text-slate-600">
              Bạn vẫn có thể phân tích thử mà không đăng nhập. Đăng nhập chỉ cần khi muốn lưu hồ sơ, lịch sử hoặc xóa dữ
              liệu cá nhân theo tài khoản.
            </p>
          </div>
        </section>

        <Card title="Tiếp tục với Google" description="Love Sense AI dùng Firebase Authentication để xác thực Google an toàn.">
          <div className="space-y-5">
            {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

            <InfoAlert>
              Ứng dụng không tự truy cập tin nhắn. Bạn chỉ phân tích nội dung do chính bạn nhập hoặc tải lên.
            </InfoAlert>

            <Button
              type="button"
              size="lg"
              className="w-full"
              isLoading={isSubmitting || loading}
              onClick={handleGoogleLogin}
              aria-label="Tiếp tục với Google"
            >
              <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white text-sm font-extrabold text-rose-600">
                G
              </span>
              {isSubmitting ? 'Đang đăng nhập' : 'Tiếp tục với Google'}
              <ArrowRight className="h-4 w-4" aria-hidden="true" />
            </Button>

            <p className="text-xs leading-5 text-slate-500">
              Firebase ID Token chỉ được gửi đến backend qua header Authorization khi bạn gọi API cần đăng nhập.
            </p>
          </div>
        </Card>
      </div>
    </PageShell>
  );
}
