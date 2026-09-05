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
  'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border-2 border-rose-950 bg-rose-600 px-6 py-3 text-sm font-extrabold text-white shadow-[5px_5px_0_rgba(127,29,29,0.24)] transition hover:-translate-y-0.5 hover:bg-rose-700 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2';

const secondaryCtaClass =
  'inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-extrabold text-slate-950 shadow-[0_12px_32px_rgba(15,23,42,0.08)] transition hover:-translate-y-0.5 hover:border-rose-300 hover:bg-rose-50 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2';

export default function HomePage() {
  return (
    <PageShell className="space-y-16 pb-16 pt-6 sm:space-y-20 sm:pt-10">
      <section className="landing-premium-bg artistic-shadow-lg relative overflow-hidden rounded-[2rem] border-2 border-slate-950 bg-white">
        <div className="pointer-events-none absolute -right-16 -top-16 h-52 w-52 rounded-full bg-rose-300/28 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 left-1/4 h-56 w-56 rounded-full bg-teal-300/18 blur-3xl" />
        <div className="relative z-10 grid gap-10 px-5 py-9 min-[390px]:px-6 sm:px-10 sm:py-14 lg:grid-cols-[1.02fr_0.98fr] lg:items-center lg:px-12 lg:py-16">
          <div className="landing-fade-up max-w-3xl space-y-8">
            <Badge tone="teal">
              <ShieldCheck className="h-3.5 w-3.5" aria-hidden="true" />
              CodeSense AI • Adaptive Programming Tutor
            </Badge>

            <div className="space-y-5">
              <h1 className="max-w-4xl font-display text-4xl font-extrabold leading-[1.08] tracking-tight text-slate-950 sm:text-5xl lg:text-6xl">
                CodeSense AI
              </h1>
              <p className="max-w-2xl text-xl font-bold text-rose-600 sm:text-2xl">
                Adaptive Programming Tutor for Beginner C# OOP Students
              </p>
              <p className="max-w-2xl text-base font-medium leading-8 text-slate-700 sm:text-lg">
                Hệ thống gia sư lập trình thích ứng hỗ trợ sinh viên học lập trình hướng đối tượng (OOP) với C#, phân tích mã nguồn, phát hiện lỗi cú pháp/logic và gợi ý hướng tư duy từng bước.
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
              {['Nhập thủ công', 'Kết quả chỉ tham khảo', 'Bạn kiểm soát dữ liệu'].map((item) => (
                <div key={item} className="flex items-center gap-2 rounded-2xl border border-rose-100 bg-white/80 px-3 py-2 shadow-sm shadow-rose-100/60">
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
              className="landing-card-hover rounded-[24px] border border-slate-200 bg-white p-5 shadow-[0_14px_38px_rgba(15,23,42,0.06)] backdrop-blur"
            >
              <Icon className="mb-4 h-5 w-5 text-rose-600" aria-hidden="true" />
              <h2 className="font-bold text-slate-950">{item.title}</h2>
              <p className="mt-2 text-sm leading-6 text-slate-600">{item.description}</p>
            </div>
          );
        })}
      </section>

      <section className="space-y-6">
        <div className="mx-auto max-w-3xl text-center">
          <Badge tone="slate">Feature blocks</Badge>
          <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-4xl">
            Một không gian rõ ràng để nhìn lại hội thoại
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-600">
            Từng phần của CodeSense AI được thiết kế để hỗ trợ học lập trình hiệu quả, phát triển tư duy giải thuật độc lập và không phụ thuộc vào code giải sẵn.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title} className="landing-card-hover">
                <span className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-rose-200 bg-rose-100 text-rose-700 shadow-sm shadow-rose-100">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </span>
                <h3 className="font-bold text-slate-950">{feature.title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{feature.description}</p>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.07)] sm:p-8">
        <div className="grid gap-8 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <Badge tone="rose">Cách hoạt động</Badge>
            <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight text-slate-950">Ba bước, không phức tạp</h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Luồng phân tích được giữ ngắn để bạn tập trung vào bối cảnh thật và cách phản hồi phù hợp.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {steps.map((step, index) => (
              <div key={step.title} className="rounded-2xl border border-slate-200 bg-slate-50 p-5 shadow-sm">
                <span className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-rose-200 bg-white font-mono text-sm font-bold text-rose-600">
                  {index + 1}
                </span>
                <h3 className="mt-4 font-bold text-slate-950">{step.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="rounded-[2rem] border border-teal-200 bg-teal-50 p-6 shadow-[0_16px_45px_rgba(15,118,110,0.08)] sm:p-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start">
          <span className="inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-teal-200 bg-white text-teal-700 shadow-sm">
            <ShieldCheck className="h-5 w-5" aria-hidden="true" />
          </span>
          <div>
            <h2 className="text-xl font-bold text-slate-950">Gia sư đồng hành, hướng dẫn tư duy từng bước</h2>
            <p className="mt-2 max-w-4xl text-base leading-7 text-slate-700">
              CodeSense AI đồng hành cùng bạn giải quyết bài tập lập trình C# OOP: phát hiện lỗi sai, đưa ra gợi ý gợi mở (Socratic tutoring) và giúp bạn tự làm chủ kiến thức.
            </p>
          </div>
        </div>
      </section>

      <section className="overflow-hidden rounded-[2rem] border-2 border-slate-950 bg-slate-950 p-6 text-white shadow-[8px_8px_0_rgba(244,63,94,0.22)] sm:p-8">
        <div className="grid gap-6 lg:grid-cols-[1fr_auto] lg:items-center">
          <div>
            <Badge tone="rose" className="border-white/10 bg-white/10 text-rose-100">
              Demo ready
            </Badge>
            <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">Bắt đầu với một đoạn chat ngắn</h2>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-300">
              Nhập vài dòng hội thoại, thêm bối cảnh cần thiết và xem gợi ý phản hồi tham khảo trong vài giây.
            </p>
          </div>
          <Link
            href="/analyze"
            className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl border-2 border-white bg-white px-6 py-3 text-sm font-extrabold text-slate-950 transition hover:-translate-y-0.5 hover:bg-rose-50 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 focus:ring-offset-slate-950 sm:w-auto"
          >
            Phân tích ngay
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
