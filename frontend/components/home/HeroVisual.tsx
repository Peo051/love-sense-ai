import { LockKeyhole, MessageCircle, ShieldCheck, Sparkles } from 'lucide-react';

import Badge from '@/components/common/Badge';

const emotionBars = [
  { label: 'mệt mỏi', value: '35%', width: 'w-[35%]' },
  { label: 'né tránh nhẹ', value: '25%', width: 'w-[25%]' },
  { label: 'trung lập', value: '20%', width: 'w-[20%]' },
];

export default function HeroVisual() {
  return (
    <div className="landing-fade-up landing-fade-delay-1 w-full min-w-0">
      <div className="landing-preview-float relative mx-auto max-w-xl">
        <div className="pointer-events-none absolute -left-8 top-8 h-28 w-28 rounded-full bg-rose-300/30 blur-3xl" />
        <div className="pointer-events-none absolute -right-6 bottom-16 h-32 w-32 rounded-full bg-teal-300/25 blur-3xl" />
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full bg-amber-200/20 blur-3xl" />

        <div className="relative overflow-hidden rounded-[2rem] border border-white/80 bg-white/90 p-4 shadow-2xl shadow-rose-200/70 ring-1 ring-white/80 backdrop-blur">
          <div className="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-rose-300/70 to-transparent" />
          <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-white/70 to-transparent" />

          <div className="relative mb-4 flex flex-col gap-3 min-[430px]:flex-row min-[430px]:items-center min-[430px]:justify-between">
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-950">Bản xem trước phân tích</p>
              <p className="text-xs text-slate-500">Nhập thủ công, không lưu mặc định</p>
            </div>
            <Badge tone="teal" className="max-w-full shrink-0 whitespace-normal text-left">
              <LockKeyhole className="h-3.5 w-3.5" aria-hidden="true" />
              Không lưu chat nếu chưa đồng ý
            </Badge>
          </div>

          <div className="relative grid gap-4">
            <div className="rounded-2xl border border-slate-100 bg-slate-50/80 p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Mock chat</p>
                <span className="hidden rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-slate-500 shadow-sm min-[390px]:inline-flex">
                  Manual input
                </span>
              </div>
              <div className="space-y-2 text-sm leading-6 text-slate-700">
                <ChatLine speaker="A" text="Em sao vậy?" />
                <ChatLine speaker="B" text="Không sao." muted />
                <ChatLine speaker="A" text="Anh thấy em hơi lạ." />
                <ChatLine speaker="B" text="Em mệt thôi." muted />
              </div>
            </div>

            <div className="rounded-2xl border border-rose-100 bg-white p-4 shadow-sm">
              <div className="mb-4 flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-rose-600">AI result</p>
                  <p className="mt-1 break-words text-lg font-bold text-slate-950">mệt mỏi / né tránh nhẹ</p>
                </div>
                <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
                  <Sparkles className="h-5 w-5 animate-pulse" aria-hidden="true" />
                </span>
              </div>

              <div className="space-y-3">
                {emotionBars.map((bar) => (
                  <div key={bar.label}>
                    <div className="mb-1 flex justify-between text-xs font-medium text-slate-600">
                      <span>{bar.label}</span>
                      <span>{bar.value}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-rose-50">
                      <div className={`h-full rounded-full bg-gradient-to-r from-rose-500 to-pink-400 ${bar.width}`} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="hidden rounded-2xl border border-teal-100 bg-teal-50/80 p-4 sm:block">
              <div className="flex gap-3">
                <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-white text-teal-700 shadow-sm">
                  <MessageCircle className="h-5 w-5" aria-hidden="true" />
                </span>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-teal-700">Gợi ý phản hồi</p>
                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    “Em nghỉ một chút nha, khi nào muốn nói anh vẫn ở đây nghe em.”
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-2xl border border-white bg-white/70 px-4 py-3 text-xs font-semibold text-slate-600 shadow-sm">
              <ShieldCheck className="h-4 w-4 text-teal-600" aria-hidden="true" />
              Kết quả chỉ mang tính tham khảo và ưu tiên quyền riêng tư.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ChatLine({ speaker, text, muted = false }: { speaker: string; text: string; muted?: boolean }) {
  return (
    <div className="flex items-start gap-2">
      <span className="mt-0.5 inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-white text-xs font-bold text-rose-600 shadow-sm">
        {speaker}
      </span>
      <span className={muted ? 'text-slate-500' : 'text-slate-800'}>{text}</span>
    </div>
  );
}
