'use client';

import { MessageCircle, ShieldAlert, TrendingUp } from 'lucide-react';

import Card from '@/components/common/Card';
import { EmptyState, ErrorState, LoadingState } from '@/components/common/StateBlocks';
import type { AnalyzeResponse } from '@/lib/types';

type Props = {
  result?: AnalyzeResponse | null;
  error?: string | null;
  loading?: boolean;
};

function formatEmotionName(name: string) {
  return name.replaceAll('_', ' ');
}

export default function AnalysisResultPanel({ result = null, error = null, loading = false }: Props) {
  if (loading) {
    return (
      <LoadingState
        title="Đang phân tích hội thoại"
        description="Backend đang tạo kết quả theo schema an toàn. Nếu LLM gặp lỗi, hệ thống sẽ dùng fallback để không làm gián đoạn trải nghiệm."
      />
    );
  }

  if (error) {
    return <ErrorState title="Không thể phân tích" description={error} />;
  }

  if (!result) {
    return (
      <EmptyState
        title="Kết quả sẽ xuất hiện tại đây"
        description="Nhập đoạn chat và bối cảnh cá nhân hóa để nhận sắc thái tổng quan, độ tin cậy, phân bố cảm xúc và gợi ý phản hồi."
      />
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);
  const distributionEntries = Object.entries(result.emotion_distribution);

  return (
    <div className="space-y-5">
      <Card title="Kết quả cảm xúc" description="Kết quả chỉ nên dùng làm gợi ý để giao tiếp nhẹ nhàng hơn.">
        <div className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-[1fr_150px]">
            <div className="rounded-2xl bg-rose-50 px-4 py-4">
              <p className="text-sm text-slate-600">Cảm xúc tổng quan</p>
              <p className="mt-1 text-2xl font-bold text-rose-700">{result.overall_emotion}</p>
            </div>
            <div className="rounded-2xl bg-slate-50 px-4 py-4">
              <p className="text-sm text-slate-600">Độ tin cậy</p>
              <p className="mt-1 text-2xl font-bold text-slate-950">{confidencePercent}%</p>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-950">
              <TrendingUp className="h-4 w-4 text-teal-600" aria-hidden="true" />
              Phân bố cảm xúc
            </div>
            {distributionEntries.map(([emotion, value]) => {
              const percent = Math.max(0, Math.min(100, Math.round(value * 100)));

              return (
                <div key={emotion} className="space-y-1.5">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="font-medium capitalize text-slate-700">{formatEmotionName(emotion)}</span>
                    <span className="tabular-nums text-slate-500">{percent}%</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-teal-500" style={{ width: `${percent}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>

      <Card title="Tóm tắt">
        <p className="text-sm leading-6 text-slate-700">{result.summary}</p>
      </Card>

      <Card title="Ghi chú theo bối cảnh">
        <p className="text-sm leading-6 text-slate-700">{result.context_note}</p>
      </Card>

      <Card title="Gợi ý phản hồi">
        <div className="flex gap-3 rounded-2xl bg-teal-50 px-4 py-4 text-teal-950">
          <MessageCircle className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm leading-6">{result.suggested_reply}</p>
        </div>
      </Card>

      <Card title="Cảnh báo an toàn" className="border-amber-200 bg-amber-50/80">
        <div className="flex gap-3 text-amber-950">
          <ShieldAlert className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm leading-6">{result.warning}</p>
        </div>
      </Card>
    </div>
  );
}
