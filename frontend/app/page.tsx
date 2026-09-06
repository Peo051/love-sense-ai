import {
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Code2,
  History,
  Lightbulb,
  LockKeyhole,
  ShieldCheck,
  Sparkles,
  Terminal,
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
    icon: Code2,
    title: 'Học chủ động',
    description: 'Nhập hoặc tải ảnh chụp đoạn mã C# OOP để nhận phân tích chi tiết.',
  },
  {
    icon: LockKeyhole,
    title: 'Bảo mật mã nguồn',
    description: 'Mã nguồn và bài tập của học viên chỉ lưu khi có consent rõ ràng.',
  },
  {
    icon: Trash2,
    title: 'Quyền kiểm soát dữ liệu',
    description: 'Xóa lịch sử thực hành, hồ sơ học tập bất cứ khi nào bạn muốn.',
  },
];

const features = [
  {
    icon: Code2,
    title: 'Gia sư thích ứng C# OOP',
    description: 'Hỗ trợ sinh viên nắm vững các khái niệm then chốt: Class, Object, Encapsulation, Inheritance, Polymorphism.',
  },
  {
    icon: Sparkles,
    title: 'Phương pháp gợi mở Socratic',
    description: 'Không đưa ngay đáp án giải sẵn; gợi ý từng bước để học viên tự nhận biết lỗi và phát triển tư duy.',
  },
  {
    icon: UserRound,
    title: 'Hồ sơ học viên cá nhân hóa',
    description: 'Lưu trình độ hiện tại và mục tiêu môn học để hệ thống điều chỉnh độ khó của gợi ý.',
  },
  {
    icon: History,
    title: 'Lịch sử thực hành & bài nộp',
    description: 'Xem lại các lỗi lập trình đã sửa và theo dõi tiến độ tiến bộ qua từng bài tập.',
  },
];

const steps = [
  {
    title: '1. Nhập hoặc quét code',
    description: 'Dán đoạn mã C# OOP hoặc tải ảnh chụp code từ màn hình IDE / bài tập giảng đường.',
  },
  {
    title: '2. Xác định vấn đề OOP',
    description: 'Mô tả vướng mắc bạn đang gặp phải: lỗi cú pháp, ngoại lệ runtime hoặc tư duy thiết kế lớp.',
  },
  {
    title: '3. Nhận gợi ý từng bước',
    description: 'Hệ thống phân tích và đưa ra gợi ý logic mở dần để bạn tự tay hoàn thiện mã nguồn.',
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
                Gia sư lập trình thích ứng dành cho sinh viên nhập môn Lập trình hướng đối tượng (OOP) C#. Hướng dẫn tư duy giải thuật, phát hiện lỗi cú pháp/logic và đưa ra gợi ý từng bước.
              </p>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row">
              <Link href="/tutor" className={`${primaryCtaClass} w-full sm:w-auto`}>
                Học cùng Gia sư AI
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </Link>
              <Link href="/privacy" className={`${secondaryCtaClass} w-full sm:w-auto`}>
                Xem quyền riêng tư
              </Link>
            </div>

            <div className="grid gap-3 text-sm font-semibold text-slate-700 sm:grid-cols-3">
              {['Học tập chủ động', 'Gợi ý từng bước Socratic', 'Bảo mật mã nguồn'].map((item) => (
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
          <Badge tone="slate">Tính năng cốt lõi</Badge>
          <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight text-slate-950 sm:text-4xl">
            Môi trường học lập trình OOP cá nhân hóa
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-600">
            CodeSense AI được thiết kế để hỗ trợ sinh viên tự tin giải quyết bài tập lập trình, thấu hiểu nguyên lý thiết kế hướng đối tượng và làm chủ kỹ năng gỡ lỗi.
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
            <Badge tone="rose">Quy trình học tập</Badge>
            <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight text-slate-950">Ba bước rèn luyện tư duy</h2>
            <p className="mt-4 text-base leading-7 text-slate-600">
              Quy trình tinh gọn giúp bạn tập trung vào bản chất bài toán và cách thiết kế cấu trúc lớp đối tượng chuẩn xác.
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
            <Lightbulb className="h-5 w-5" aria-hidden="true" />
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
              C# OOP Tutor
            </Badge>
            <h2 className="mt-4 font-display text-3xl font-extrabold leading-tight tracking-tight sm:text-4xl">Bắt đầu buổi học lập trình C#</h2>
            <p className="mt-3 max-w-2xl text-base leading-7 text-slate-300">
              Dán đoạn code bài tập hoặc tải ảnh đề bài để nhận gợi ý hướng dẫn từ Gia sư CodeSense AI.
            </p>
          </div>
          <Link
            href="/tutor"
            className="inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl border-2 border-white bg-white px-6 py-3 text-sm font-extrabold text-slate-950 transition hover:-translate-y-0.5 hover:bg-rose-50 focus:outline-none focus:ring-4 focus:ring-rose-100 focus:ring-offset-2 focus:ring-offset-slate-950 sm:w-auto"
          >
            Trải nghiệm Gia sư AI
            <ArrowRight className="h-4 w-4" aria-hidden="true" />
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
