import {
  ArrowRight,
  CheckCircle2,
  HeartHandshake,
  History,
  LockKeyhole,
  MessageSquareText,
  ShieldCheck,
  Sparkles,
  Trash2,
  UserRound,
} from 'lucide-react';
import Link from 'next/link';

import Badge from '@/components/common/Badge';
import Card from '@/components/common/Card';
import HeroVisual from '@/components/home/HeroVisual';
import PageShell from '@/components/common/PageShell';

const trustItems = [
  {
    icon: MessageSquareText,
    title: 'Nhập thủ công',
    description: 'Bạn tự nhập đoạn hội thoại cần xem lại.',
  },
  {
    icon: LockKeyhole,
    title: 'Không lưu mặc định',
    description: 'Nội dung chat chỉ lưu khi bạn đồng ý rõ ràng.',
  },
  {
    icon: Trash2,
    title: 'Có quyền xóa dữ liệu',
    description: 'Xóa lịch sử, hồ sơ hoặc toàn bộ dữ liệu bất cứ lúc nào.',
  },
];

const features = [
  {
    icon: HeartHandshake,
    title: 'Phân tích sắc thái hội thoại',
    description: 'Nhận định các tín hiệu cảm xúc có thể xuất hiện trong đoạn chat, luôn kèm độ tin cậy và cảnh báo an toàn.',
  },
  {
    icon: Sparkles,
    title: 'Gợi ý phản hồi nhẹ nhàng',
    description: 'Ưu tiên cách trả lời bình tĩnh, tôn trọng, không gây áp lực và không thao túng cảm xúc.',
  },
  {
    icon: UserRound,
    title: 'Hồ sơ cá nhân hóa',
    description: 'Thêm phong cách giao tiếp, thói quen phản hồi và bối cảnh riêng để gợi ý phù hợp hơn.',
  },
  {
    icon: History,
    title: 'Lịch sử có consent',
    description: 'Chỉ lưu kết quả hoặc chat gốc khi bạn bật tùy chọn đồng ý lưu dữ liệu.',
  },
];

const steps = [
  {
    title: 'Nhập đoạn chat',
    description: 'Dán hoặc nhập thủ công vài dòng hội thoại bạn muốn nhìn lại một cách bình tĩnh.',
  },
  {
    title: 'Thêm bối cảnh',
    description: 'Bổ sung phong cách giao tiếp, trạng thái hoặc điều cần lưu ý để kết quả bớt máy móc.',
  },
  {
    title: 'Nhận phân tích tham khảo',
    description: 'Xem sắc thái tổng quan, phân bố cảm xúc và một gợi ý phản hồi nhẹ nhàng.',
  },
];

const primaryCtaClass =
  'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border-2 border-slate-950 bg-blue-600 px-6 py-3 text-sm font-black text-white shadow-[6px_6px_0_#111827] transition hover:-translate-y-0.5 hover:bg-violet-600 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2';

const secondaryCtaClass =
  'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border-2 border-slate-950 bg-white px-6 py-3 text-sm font-black text-slate-950 shadow-[5px_5px_0_rgba(17,24,39,0.18)] transition hover:-translate-y-0.5 hover:bg-blue-50 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2';

export default function HomePage() {
  return (
    <PageShell className="space-y-16 pb-16 pt-6 sm:space-y-20 sm:pt-10">
      <section className="landing-premium-bg artistic-shadow-lg relative overflow-hidden rounded-[2rem] border-2 border-slate-950 bg-white">
        <div className="pointer-events-none absolute -right-16 -top-16 h-52 w-52 rounded-full bg-violet-400/30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 left-1/4 h-56 w-56 rounded-full bg-blue-400/20 blur-3xl" />
        <div className="relative z-10 grid gap-10 px-5 py-9 min-[390px]:px-6 sm:px-10 sm:py-14 lg:grid-cols-[1.02fr_0.98fr] lg:items-center lg:px-12 lg:py-16">
          <div className="landing-fade-up max-w-3xl space-y-8">
            <Badge tone="teal">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
              Privacy-first • Manual input • Consent-based
            </Badge>

            <div className="space-y-5">
              <h1 className="max-w-4xl font-display text-5xl font-normal leading-[0.98] text-slate-950 sm:text-6xl lg:text-7xl">
                Hiểu sắc thái hội thoại. Phản hồi bình tĩnh hơn.
              </h1>
              <p className="max-w-2xl text-base font-medium leading-8 text-slate-700 sm:text-lg">
                Nhập đoạn chat thủ công, kiểm tra nội dung trích xuất từ ảnh và nhận gợi ý phản hồi tham khảo — không đọc
                trộm, không lưu mặc định.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Link href="/analyze" className={`${primaryCtaClass} w-full sm:w-auto`}>
                Bắt đầu phân tích
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link href="/privacy" className={`${secondaryCtaClass} w-full sm:w-auto`}>
                Xem quyền riêng tư
              </Link>
            </div>

            <div className="grid gap-3 text-sm font-semibold text-slate-700 sm:grid-cols-3">
              {['Không đọc trộm tin nhắn', 'Kết quả chỉ tham khảo', 'Bạn kiểm soát dữ liệu'].map((item) => (
                <div key={item} className="flex items-center gap-2 rounded-2xl border-2 border-slate-950 bg-white/80 px-3 py-2">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" aria-hidden="true" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          <HeroVisual />
        </div>
      </section>

      <section className="landing-fade-up landing-fade-delay-2 grid gap-3 md:grid-cols-3">
        {trustItems.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.title}
              className="landing-card-hover rounded-[24px] border-2 border-slate-950 bg-white p-5 shadow-[5px_5px_0_rgba(17,24,39,0.14)] backdrop-blur"
            >
              <Icon className="mb-4 h-5 w-5 text-blue-600" aria-hidden="true" />
              <h2 className="font-black text-slate-950">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
            </div>
          );
        })}
      </section>

      <section className="space-y-6">
        <div className="mx-auto max-w-3xl text-center">
          <Badge tone="slate">Feature blocks</Badge>
          <h2 className="mt-4 font-display text-4xl font-normal leading-tight text-slate-950 sm:text-5xl">
            Một không gian rõ ràng để nhìn lại hội thoại
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-600">
            Từng phần của Love Sense AI được thiết kế để hỗ trợ giao tiếp tốt hơn, không phán xét và không thay thế trao
            đổi trực tiếp.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="landing-card-hover">
                <span className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-2xl border-2 border-slate-950 bg-blue-100 text-blue-700 shadow-[4px_4px_0_rgba(17,24,39,0.16)]">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <h3 className="font-black text-slate-950">{feature.title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="rounded-[2rem] border-2 border-slate-950 bg-white p-6 shadow-[8px_8px_0_rgba(17,24,39,0.14)] sm:p-8">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <Badge tone="rose">Cách hoạt động</Badge>
            <h2 className="mt-4 font-display text-4xl font-normal leading-tight text-slate-950">Ba bước, không phức tạp</h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Luồng phân tích được giữ ngắn để bạn tập trung vào bối cảnh thật và cách phản hồi phù hợp.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step.title} className="rounded-2xl border-2 border-slate-950 bg-slate-50 p-5 shadow-[4px_4px_0_rgba(17,24,39,0.12)]">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full border-2 border-slate-950 bg-white font-mono text-sm font-bold text-blue-600">
                  {index + 1}
                </span>
                <h3 className="mt-4 font-black text-slate-950">{step.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-[2rem] border-2 border-slate-950 bg-emerald-50 p-6 shadow-[8px_8px_0_rgba(17,24,39,0.12)] sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
          <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border-2 border-slate-950 bg-white text-emerald-700 shadow-[4px_4px_0_rgba(17,24,39,0.14)]">
            <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 className="text-xl font-black text-slate-950">Giao tiếp tốt hơn, không kết luận thay bạn</h2>
            <p className="mt-2 max-w-4xl text-base leading-7 text-slate-700">
              Love Sense AI không kết luận chắc chắn cảm xúc của người khác. Kết quả chỉ hỗ trợ bạn giao tiếp bình tĩnh
              và tôn trọng hơn.
            </p>
          </div>
        </div>
      </section>

      <section className="overflow-hidden rounded-[2rem] border-2 border-slate-950 bg-slate-950 p-6 text-white shadow-[10px_10px_0_rgba(59,130,246,0.28)] sm:p-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <Badge tone="rose" className="border-white/10 bg-white/10 text-rose-100">
              Demo ready
            </Badge>
            <h2 className="mt-4 font-display text-4xl font-normal leading-tight sm:text-5xl">Bắt đầu với một đoạn chat ngắn</h2>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-300">
              Nhập vài dòng hội thoại, thêm bối cảnh cần thiết và xem gợi ý phản hồi tham khảo trong vài giây.
            </p>
          </div>
          <Link
            href="/analyze"
            className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl border-2 border-white bg-white px-6 py-3 text-sm font-black text-slate-950 transition hover:-translate-y-0.5 hover:bg-blue-50 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2 focus:ring-offset-slate-950 sm:w-auto"
          >
            Phân tích ngay
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
