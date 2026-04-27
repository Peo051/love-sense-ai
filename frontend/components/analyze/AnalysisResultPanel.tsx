'use client';

import {
  AlertTriangle,
  BarChart3,
  HeartHandshake,
  Info,
  MessageCircle,
  Quote,
  RotateCcw,
  ShieldAlert,
  Sparkles,
} from 'lucide-react';

import Card from '@/components/common/Card';
import type { AnalyzeResponse } from '@/lib/types';

type Props = {
  result?: AnalyzeResponse | null;
  error?: string | null;
  loading?: boolean;
};

function formatEmotionName(name: string) {
  return name.replaceAll('_', ' ');
}

function clampPercent(value: number) {
  return Math.max(0, Math.min(100, Math.round(value * 100)));
}

function SkeletonLine({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-full bg-slate-200/80 ${className}`} />;
}

export default function AnalysisResultPanel({ result = null, error = null, loading = false }: Props) {
  if (loading) {
    return (
      <div role="status" aria-live="polite" className="space-y-4">
        <Card className="bg-white">
          <div className="flex items-start gap-3">
            <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-rose-100 text-rose-600">
              <Sparkles className="h-5 w-5 animate-pulse" aria-hidden="true" />
            </span>
            <div>
              <h2 className="text-lg font-semibold text-slate-950">Đang phân tích sắc thái hội thoại</h2>
              <p className="mt-1 text-sm leading-6 text-slate-600">
                Hệ thống đang đọc tín hiệu cảm xúc, đối chiếu bối cảnh và chuẩn bị gợi ý phản hồi an toàn.
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="space-y-5">
            <SkeletonLine className="h-6 w-2/3" />
            <SkeletonLine className="h-12 w-full rounded-2xl" />
            <SkeletonLine className="h-3 w-full" />
            <SkeletonLine className="h-3 w-5/6" />
            <SkeletonLine className="h-3 w-4/6" />
          </div>
        </Card>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card>
            <SkeletonLine className="h-4 w-24" />
            <SkeletonLine className="mt-4 h-20 w-full rounded-2xl" />
          </Card>
          <Card>
            <SkeletonLine className="h-4 w-28" />
            <SkeletonLine className="mt-4 h-20 w-full rounded-2xl" />
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-100 bg-red-50/80">
        <div role="alert" className="flex gap-3 text-red-900">
          <AlertTriangle className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-semibold">Chưa thể tạo kết quả</h2>
            <p className="mt-2 text-sm leading-6">{error}</p>
            <div className="mt-4 rounded-2xl border-2 border-red-900 bg-white/70 p-4 text-sm leading-6 text-red-800 shadow-[4px_4px_0_rgba(127,29,29,0.12)]">
              <p className="font-semibold">Bạn có thể thử:</p>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                <li>Kiểm tra backend đang chạy và có thể nhận request.</li>
                <li>Giữ nguyên nội dung đã nhập, chờ vài giây rồi bấm phân tích lại.</li>
                <li>Nếu dùng local, kiểm tra biến `NEXT_PUBLIC_API_URL` của frontend.</li>
              </ul>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="border-dashed bg-rose-50/70">
        <div className="flex min-h-[24rem] flex-col justify-center px-1 py-6 text-center sm:min-h-[34rem] sm:px-6">
          <div className="mx-auto mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl border border-slate-200 bg-white text-rose-600 shadow-sm">
            <HeartHandshake className="h-7 w-7" aria-hidden="true" />
          </div>
          <h2 className="text-lg font-bold text-slate-950 sm:text-xl">Kết quả phân tích sẽ xuất hiện ở đây</h2>
          <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-slate-600">
            Nhập đoạn chat ngắn ở cột bên trái để xem sắc thái tổng quan, độ tin cậy, phân bố cảm xúc và gợi ý phản hồi.
          </p>

          <div className="mx-auto mt-6 max-w-md rounded-2xl border border-slate-200 bg-white/80 p-4 text-left shadow-sm">
            <p className="font-mono text-xs font-bold uppercase tracking-[0.16em] text-rose-600">Gợi ý mẫu</p>
            <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-700">
              A: Em sao vậy?{'\n'}B: Không sao.{'\n'}A: Anh thấy em hơi lạ.{'\n'}B: Em mệt thôi.
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const confidencePercent = clampPercent(result.confidence);
  const distributionEntries = Object.entries(result.emotion_distribution);
  const evidenceItems = result.evidence ?? [];
  const uncertaintyItems = result.uncertainty_reasons ?? [];
  const inputQuality = result.input_quality ?? 'medium';
  const shouldWarnInputQuality = inputQuality === 'low';

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden bg-[linear-gradient(135deg,#fff1f2_0%,#ffffff_52%,#ccfbf1_100%)]" variant="artistic">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="font-mono text-sm font-bold uppercase tracking-[0.16em] text-rose-700">Analysis board</p>
            <h2 className="mt-2 break-words font-display text-3xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-4xl">
              {result.overall_emotion}
            </h2>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
              Đây là tín hiệu tham khảo để bạn chọn cách phản hồi bình tĩnh hơn, không phải kết luận chắc chắn.
            </p>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white/90 p-4 shadow-sm sm:min-w-40">
            <p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-slate-600">Độ tin cậy</p>
            <p className="mt-1 text-3xl font-black text-emerald-700">{confidencePercent}%</p>
          </div>
        </div>
      </Card>

      <Card title="Confidence meter" description="Mức này thể hiện độ chắc tương đối của phân tích, không phải sự thật tuyệt đối.">
        <div className="h-3 overflow-hidden rounded-full bg-slate-100">
          <div
            className="h-full rounded-full bg-gradient-to-r from-rose-500 to-rose-700 transition-all duration-300"
            style={{ width: `${confidencePercent}%` }}
          />
        </div>
        <div className="mt-2 flex justify-between text-xs font-medium text-slate-500">
          <span>Thấp</span>
          <span>Trung bình</span>
          <span>Cao</span>
        </div>
      </Card>

      {shouldWarnInputQuality ? (
        <Card title="Chất lượng đầu vào cần kiểm tra" className="border-amber-200 bg-amber-50/80">
          <div className="flex gap-3 text-amber-950">
            <Info className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
            <p className="text-sm leading-6">
              Đoạn chat có thể quá ngắn hoặc OCR chưa rõ. Hãy kiểm tra lại nội dung trước khi dùng kết quả để phản hồi.
            </p>
          </div>
        </Card>
      ) : null}

      {result.tone || result.reply_style ? (
        <Card title="Sắc thái & cách phản hồi">
          <div className="grid gap-4 sm:grid-cols-2">
            {result.tone ? (
              <div className="rounded-2xl border border-slate-200 bg-rose-50/80 p-4">
                <p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-rose-700">Sắc thái</p>
                <p className="mt-2 text-sm leading-6 text-slate-700">{result.tone}</p>
              </div>
            ) : null}
            {result.reply_style ? (
              <div className="rounded-2xl border border-slate-200 bg-emerald-50/80 p-4">
                <p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-emerald-700">Phong cách gợi ý</p>
                <p className="mt-2 text-sm leading-6 text-slate-700">{result.reply_style}</p>
              </div>
            ) : null}
          </div>
        </Card>
      ) : null}

      <Card title="Phân bố cảm xúc" description="Các nhóm cảm xúc có thể cùng xuất hiện trong một đoạn hội thoại.">
        <div className="space-y-4">
          {distributionEntries.map(([emotion, value]) => {
            const percent = clampPercent(value);

            return (
              <div key={emotion} className="space-y-1.5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="flex min-w-0 items-center gap-2 font-medium capitalize text-slate-700">
                    <BarChart3 className="h-4 w-4 text-rose-600" aria-hidden="true" />
                    <span className="break-words">{formatEmotionName(emotion)}</span>
                  </span>
                  <span className="tabular-nums text-slate-500">{percent}%</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-100">
                  <div className="h-full rounded-full bg-rose-600" style={{ width: `${percent}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Tóm tắt">
          <p className="text-sm leading-6 text-slate-700">{result.summary}</p>
        </Card>

        <Card title="Ghi chú theo bối cảnh">
          <p className="text-sm leading-6 text-slate-700">{result.context_note}</p>
        </Card>
      </div>

      {evidenceItems.length > 0 ? (
        <Card title="Câu làm căn cứ" description="Các câu này chỉ là tín hiệu tham khảo, không phải bằng chứng kết luận cảm xúc thật.">
          <div className="space-y-3">
            {evidenceItems.map((item, index) => (
              <div key={`${item.quote}-${index}`} className="flex gap-3 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 shadow-sm">
                <Quote className="mt-1 h-4 w-4 shrink-0 text-rose-600" aria-hidden="true" />
                <div>
                  <p className="font-mono text-xs font-bold uppercase tracking-[0.14em] text-rose-600">{item.label}</p>
                  <p className="mt-1 whitespace-pre-line text-sm leading-6 text-slate-800">{item.quote}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{item.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      {uncertaintyItems.length > 0 ? (
        <Card title="Điểm cần thận trọng" className="border-amber-200 bg-amber-50/80">
          <ul className="space-y-2 text-sm leading-6 text-amber-950">
            {uncertaintyItems.map((item, index) => (
              <li key={`${item}-${index}`} className="flex gap-2">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" aria-hidden="true" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}

      <Card title="Gợi ý phản hồi" className="bg-emerald-50/80">
        <div className="flex gap-3 rounded-2xl border border-slate-200 bg-white/90 px-4 py-4 text-emerald-950 shadow-sm">
          <MessageCircle className="mt-1 h-5 w-5 shrink-0 text-emerald-700" aria-hidden="true" />
          <p className="text-sm leading-6">{result.suggested_reply}</p>
        </div>
      </Card>

      <Card title="Cảnh báo an toàn" className="border-amber-200 bg-amber-50/80">
        <div className="flex gap-3 text-amber-950">
          <ShieldAlert className="mt-1 h-5 w-5 shrink-0" aria-hidden="true" />
          <div>
            <p className="text-sm leading-6">{result.warning}</p>
            <p className="mt-2 flex items-center gap-2 text-sm leading-6">
              <RotateCcw className="h-4 w-4 shrink-0" aria-hidden="true" />
              Nếu cảm thấy chưa đúng bối cảnh, hãy chỉnh phần bối cảnh cá nhân hóa rồi phân tích lại.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
