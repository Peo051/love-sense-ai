import { ArrowRight, Brain, LockKeyhole, MessageSquareText, ShieldCheck, Sparkles, Trash2 } from 'lucide-react';
import Link from 'next/link';

import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import PageShell from '@/components/common/PageShell';

const features = [
  {
    icon: MessageSquareText,
    title: 'Nhập thủ công',
    description: 'Bạn tự nhập đoạn hội thoại cần xem lại. Ứng dụng không đọc trộm tin nhắn, thông báo hay danh bạ.',
  },
  {
    icon: LockKeyhole,
    title: 'Không lưu mặc định',
    description: 'Nội dung chat chỉ được lưu khi bạn bật consent rõ ràng cho từng lần phân tích.',
  },
  {
    icon: Sparkles,
    title: 'Gợi ý phản hồi nhẹ nhàng',
    description: 'Kết quả tập trung vào cách giao tiếp bình tĩnh, tôn trọng và không thao túng cảm xúc.',
  },
  {
    icon: Trash2,
    title: 'Có quyền xóa dữ liệu',
    description: 'Bạn có thể xóa lịch sử, hồ sơ cá nhân hóa hoặc toàn bộ dữ liệu của tài khoản.',
  },
];

const steps = [
  'Nhập đoạn chat',
  'Thêm bối cảnh cá nhân hóa',
  'Nhận phân tích và gợi ý phản hồi',
];

export default function HomePage() {
  return (
    <PageShell className="space-y-14">
      <section className="overflow-hidden rounded-[2rem] border border-rose-100 bg-white shadow-sm shadow-rose-100">
        <div className="grid gap-0 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-8 px-6 py-10 sm:px-10 lg:py-16">
            <Badge tone="rose">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
              Ưu tiên quyền riêng tư
            </Badge>
            <div className="space-y-5">
              <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">
                Love Sense AI
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-slate-600">
                Phân tích sắc thái hội thoại do bạn chủ động nhập và gợi ý cách phản hồi nhẹ nhàng. Kết quả chỉ mang
                tính tham khảo, không kết luận chắc chắn về cảm xúc của người khác.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link href="/analyze">
                <Button className="w-full sm:w-auto">
                  Bắt đầu phân tích
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Button>
              </Link>
              <Link href="/privacy">
                <Button variant="secondary" className="w-full sm:w-auto">
                  Xem quyền riêng tư
                </Button>
              </Link>
            </div>
          </div>

          <div className="border-t border-rose-100 bg-rose-50/50 p-5 sm:p-8 lg:border-l lg:border-t-0">
            <div className="rounded-3xl border border-white bg-white/90 p-5 shadow-sm">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-950">Bản xem nhanh</p>
                  <p className="text-xs text-slate-500">Một kết quả phân tích tham khảo</p>
                </div>
                <Badge tone="teal">Không lưu chat</Badge>
              </div>
              <div className="space-y-4">
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="text-xs font-semibold uppercase text-slate-500">Đoạn hội thoại</p>
                  <p className="mt-2 whitespace-pre-line text-sm leading-6 text-slate-700">
                    A: Em sao vậy?{'\n'}B: Không sao.{'\n'}A: Anh thấy em hơi lạ.{'\n'}B: Em mệt thôi.
                  </p>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <div className="rounded-2xl bg-rose-50 p-4">
                    <p className="text-xs font-semibold uppercase text-rose-600">Sắc thái</p>
                    <p className="mt-2 font-semibold text-slate-950">mệt mỏi / né tránh nhẹ</p>
                  </div>
                  <div className="rounded-2xl bg-teal-50 p-4">
                    <p className="text-xs font-semibold uppercase text-teal-700">Độ tin cậy</p>
                    <p className="mt-2 font-semibold text-slate-950">72%</p>
                  </div>
                </div>
                <div className="rounded-2xl bg-amber-50 p-4">
                  <p className="text-xs font-semibold uppercase text-amber-700">Gợi ý phản hồi</p>
                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Card key={feature.title}>
              <Icon className="mb-4 h-6 w-6 text-rose-600" aria-hidden="true" />
              <h2 className="font-semibold text-slate-950">{feature.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{feature.description}</p>
            </Card>
          );
        })}
      </section>

      <section className="rounded-[2rem] border border-rose-100 bg-white p-6 shadow-sm sm:p-8">
        <div className="mb-8 flex items-center gap-3">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl bg-rose-600 text-white">
            <Brain className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.18em] text-rose-600">Cách hoạt động</p>
            <h2 className="text-2xl font-bold text-slate-950">Một luồng phân tích rõ ràng trong 3 bước</h2>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {steps.map((step, index) => (
            <div key={step} className="rounded-2xl border border-slate-100 bg-slate-50 p-5">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-white text-sm font-bold text-rose-600 shadow-sm">
                {index + 1}
              </span>
              <h3 className="mt-4 font-semibold text-slate-950">{step}</h3>
              <p className="mt-2 text-sm leading-6 text-slate-600">
                {index === 0 && 'Dán hoặc nhập thủ công đoạn hội thoại bạn muốn xem lại.'}
                {index === 1 && 'Thêm bối cảnh giao tiếp để kết quả phù hợp hơn với tình huống.'}
                {index === 2 && 'Xem sắc thái, độ tin cậy, phân bố cảm xúc và gợi ý phản hồi.'}
              </p>
            </div>
          ))}
        </div>
      </section>
    </PageShell>
  );
}
