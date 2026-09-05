'use client';

import {
  Award,
  BookCheck,
  CheckCircle2,
  Clock,
  Code2,
  Cpu,
  GraduationCap,
  Layers,
  Sparkles,
} from 'lucide-react';
import Link from 'next/link';

import AuthRequiredState, { AuthLoadingState } from '@/components/auth/AuthRequiredState';
import Badge from '@/components/common/Badge';
import Card from '@/components/common/Card';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { useAuth } from '@/contexts/AuthContext';

const learningModules = [
  {
    title: '1. Lớp & Đối tượng (Classes & Objects)',
    description: 'Khai báo class, khởi tạo instance với từ khóa new, quản lý constructor.',
    status: 'completed',
    level: 'Cơ bản',
    progress: '100%',
  },
  {
    title: '2. Tính đóng gói (Encapsulation)',
    description: 'Access modifiers (private, public), Properties (get/set), bảo toàn trạng thái dữ liệu.',
    status: 'in_progress',
    level: 'Cốt lõi',
    progress: '65%',
  },
  {
    title: '3. Tính kế thừa (Inheritance)',
    description: 'Kế thừa lớp cơ sở (base class), từ khóa base, protected access modifier.',
    status: 'not_started',
    level: 'Trung bình',
    progress: '0%',
  },
  {
    title: '4. Tính đa hình & Interface (Polymorphism & Interfaces)',
    description: 'Virtual, override, abstract classes, định nghĩa và thực thi interface.',
    status: 'not_started',
    level: 'Nâng cao',
    progress: '0%',
  },
  {
    title: '5. Xử lý ngoại lệ trong OOP (Exception Handling)',
    description: 'Try-catch-finally, tự định nghĩa exception class nghiệp vụ.',
    status: 'not_started',
    level: 'Ứng dụng',
    progress: '0%',
  },
];

export default function ProgressPage() {
  const { isAuthenticated, loading } = useAuth();

  return (
    <PageShell className="space-y-8 pb-12">
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.12),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="Student Learning Analytics"
            title="Tiến độ học tập C# OOP"
            description="Theo dõi mức độ thành thạo các chủ đề Lập trình hướng đối tượng, số lượng bài tập đã thực hành và lộ trình kỹ năng tiếp theo."
          />
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <Badge tone="rose">
              <GraduationCap className="h-3.5 w-3.5" aria-hidden="true" />
              C# OOP Pathway
            </Badge>
            <Badge tone="teal">
              <Award className="h-3.5 w-3.5" aria-hidden="true" />
              Kỹ năng thích ứng
            </Badge>
          </div>
        </div>
      </section>

      {loading ? (
        <AuthLoadingState />
      ) : !isAuthenticated ? (
        <AuthRequiredState
          title="Đăng nhập để xem tiến độ học tập"
          description="Tiến độ các chủ đề C# OOP và lịch sử hoàn thành bài tập được lưu gắn liền với tài khoản của bạn."
        />
      ) : (
        <div className="space-y-8">
          {/* Quick Metrics */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Chủ đề hoàn thành</span>
                <BookCheck className="h-5 w-5 text-emerald-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">1 / 5</p>
              <p className="mt-1 text-xs text-slate-500">Lớp & Đối tượng</p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Đang luyện tập</span>
                <Clock className="h-5 w-5 text-rose-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">Tính đóng gói</p>
              <p className="mt-1 text-xs text-slate-500">Tiến độ 65%</p>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Mức độ độc lập tư duy</span>
                <Sparkles className="h-5 w-5 text-teal-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">Khá tốt</p>
              <p className="mt-1 text-xs text-slate-500">Cần trung bình 2 gợi ý / bài</p>
            </div>
          </div>

          {/* Detailed Topic Cards */}
          <Card
            title="Lộ trình kiến thức C# OOP"
            description="Các chủ đề lập trình hướng đối tượng từ cơ bản đến nâng cao được hỗ trợ bởi CodeSense AI."
          >
            <div className="space-y-4">
              {learningModules.map((module) => (
                <div
                  key={module.title}
                  className="rounded-2xl border border-slate-200 bg-white p-5 transition hover:border-rose-200 hover:shadow-sm"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-slate-950">{module.title}</h3>
                        <Badge
                          tone={
                            module.status === 'completed'
                              ? 'teal'
                              : module.status === 'in_progress'
                              ? 'rose'
                              : 'slate'
                          }
                        >
                          {module.status === 'completed'
                            ? 'Đã hoàn thành'
                            : module.status === 'in_progress'
                            ? 'Đang học'
                            : 'Chưa bắt đầu'}
                        </Badge>
                      </div>
                      <p className="mt-1 text-sm text-slate-600">{module.description}</p>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <span className="font-mono text-sm font-bold text-slate-900">{module.progress}</span>
                      </div>
                      <Link
                        href="/tutor"
                        className="inline-flex min-h-9 items-center justify-center rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-1.5 text-xs font-bold text-slate-800 transition hover:bg-rose-50 hover:text-rose-700"
                      >
                        Luyện tập
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </PageShell>
  );
}
