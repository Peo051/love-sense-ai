'use client';

import { AlertTriangle, HeartHandshake, MessageCircle, ShieldAlert } from 'lucide-react';

import Card from '@/components/common/Card';
import type { AnalyzeResponse } from '@/lib/types';

interface AnalysisResultPanelProps {
  result: AnalyzeResponse | null;
  errorMessage: string;
}

function formatEmotionName(name: string) {
  return name.replaceAll('_', ' ');
}

export default function AnalysisResultPanel({ result, errorMessage }: AnalysisResultPanelProps) {
  if (errorMessage) {
    return (
      <Card title="Không thể phân tích" className="border-red-100 bg-red-50">
        <div className="flex gap-3 text-red-800">
          <AlertTriangle className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm leading-6">{errorMessage}</p>
        </div>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card title="Kết quả phân tích" description="Kết quả mock sẽ xuất hiện ở đây sau khi gửi đoạn chat.">
        <div className="flex min-h-80 flex-col items-center justify-center rounded-lg border border-dashed border-rose-200 bg-rose-50/60 px-6 text-center">
          <HeartHandshake className="mb-4 h-10 w-10 text-rose-500" aria-hidden="true" />
          <p className="max-w-md text-sm leading-6 text-slate-600">
            Nhập đoạn chat và bối cảnh cá nhân hóa để nhận phân tích cảm xúc, gợi ý phản hồi nhẹ nhàng và
            cảnh báo an toàn.
          </p>
        </div>
      </Card>
    );
  }

  const confidencePercent = Math.round(result.confidence * 100);
  const distributionEntries = Object.entries(result.emotion_distribution);

  return (
    <div className="space-y-5">
      <Card title="Kết quả cảm xúc">
        <div className="space-y-5">
          <div className="flex flex-col gap-3 rounded-lg bg-rose-50 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-slate-600">Cảm xúc tổng quan</p>
              <p className="mt-1 text-2xl font-bold text-rose-700">{result.overall_emotion}</p>
            </div>
            <div className="rounded-md bg-white px-4 py-3 text-left shadow-sm sm:text-right">
              <p className="text-sm text-slate-600">Độ tin cậy</p>
              <p className="text-xl font-bold text-slate-950">{confidencePercent}%</p>
            </div>
          </div>

          <div className="space-y-3">
            {distributionEntries.map(([emotion, value]) => {
              const percent = Math.round(value * 100);

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
        <div className="flex gap-3 rounded-lg bg-teal-50 px-4 py-4 text-teal-950">
          <MessageCircle className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm leading-6">{result.suggested_reply}</p>
        </div>
      </Card>

      <Card title="Cảnh báo an toàn" className="border-amber-200 bg-amber-50">
        <div className="flex gap-3 text-amber-950">
          <ShieldAlert className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <p className="text-sm leading-6">{result.warning}</p>
        </div>
      </Card>
    </div>
  );
}
