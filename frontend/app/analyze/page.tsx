'use client';

import { useState } from 'react';
import { LockKeyhole, MessageSquareText, ShieldCheck, Sparkles } from 'lucide-react';

import AnalysisForm from '@/components/analyze/AnalysisForm';
import AnalysisResultPanel from '@/components/analyze/AnalysisResultPanel';
import { InfoAlert, SuccessAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { useAuth } from '@/contexts/AuthContext';
import { analyzeEmotion } from '@/lib/api';
import type { AnalyzeRequest, AnalyzeResponse } from '@/lib/types';

export default function AnalyzePage() {
  const { isAuthenticated } = useAuth();
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (payload: AnalyzeRequest) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const analysis = await analyzeEmotion(payload);
      setResult(analysis);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Không thể phân tích đoạn chat lúc này.';
      setErrorMessage(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageShell className="space-y-8 pb-12">
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.14),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="AI dashboard"
            title="Phân tích sắc thái hội thoại"
            description="Nhập đoạn chat thủ công, thêm bối cảnh cần thiết và nhận gợi ý phản hồi tham khảo. Love Sense AI không tự truy cập tin nhắn và không lưu chat nếu bạn chưa đồng ý."
          />
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <Badge tone="rose">
              <MessageSquareText className="h-3.5 w-3.5" aria-hidden="true" />
              Manual input
            </Badge>
            <Badge tone="teal">
              <LockKeyhole className="h-3.5 w-3.5" aria-hidden="true" />
              Consent-based
            </Badge>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.96fr)_minmax(420px,1.04fr)] lg:items-start">
        <div className="space-y-4 lg:sticky lg:top-24">
          {!isAuthenticated ? (
            <InfoAlert>
              Đăng nhập để lưu lịch sử và hồ sơ cá nhân hóa. Bạn vẫn có thể phân tích thử mà không cần tài khoản.
            </InfoAlert>
          ) : result?.saved_to_history ? (
            <SuccessAlert>Kết quả đã được lưu vào lịch sử theo consent của bạn.</SuccessAlert>
          ) : null}

          <div className="hidden rounded-2xl border border-slate-200 bg-white/95 p-4 shadow-sm lg:block">
            <div className="flex items-start gap-3">
              <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-rose-100 text-rose-700">
                <Sparkles className="h-5 w-5" aria-hidden="true" />
              </span>
              <div>
                <p className="text-sm font-semibold text-slate-950">Phiên phân tích riêng tư</p>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  Form giữ nội dung bạn nhập khi API lỗi. Chat gốc chỉ được gửi lưu khi bạn bật consent rõ ràng.
                </p>
              </div>
            </div>
          </div>

          <AnalysisForm isLoading={isLoading} onAnalyze={handleAnalyze} />
        </div>

        <div className="lg:sticky lg:top-24">
          <AnalysisResultPanel result={result} error={errorMessage} loading={isLoading} />
        </div>
      </div>

      <div className="rounded-2xl border border-teal-200 bg-teal-50 p-4 text-sm leading-6 text-teal-950 shadow-sm">
        <div className="flex gap-3">
          <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-emerald-700" aria-hidden="true" />
          <p>
            Phần phân tích chỉ là điểm bắt đầu để bạn giao tiếp bình tĩnh hơn, không thay thế trao đổi trực tiếp.
          </p>
        </div>
      </div>
    </PageShell>
  );
}
