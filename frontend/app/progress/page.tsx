'use client';

import { useEffect, useState } from 'react';
import {
  AlertCircle,
  ArrowRight,
  Award,
  BookCheck,
  BookOpen,
  CheckCircle2,
  Clock,
  Code2,
  Cpu,
  GraduationCap,
  History,
  Info,
  Layers,
  Lightbulb,
  Loader2,
  RefreshCw,
  Sparkles,
  Target,
  TrendingUp,
} from 'lucide-react';
import Link from 'next/link';

import AuthRequiredState, { AuthLoadingState } from '@/components/auth/AuthRequiredState';
import { ErrorAlert, InfoAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { useAuth } from '@/contexts/AuthContext';
import { getProgressDashboard } from '@/lib/api';
import type { SkillMasteryResponse, StudentProgressDashboardResponse } from '@/lib/types';

export default function ProgressPage() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [dashboardData, setDashboardData] = useState<StudentProgressDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated) return;

    let isMounted = true;
    setIsLoading(true);
    setErrorMessage(null);

    getProgressDashboard()
      .then((data) => {
        if (isMounted) {
          setDashboardData(data);
        }
      })
      .catch((err: any) => {
        if (isMounted) {
          setErrorMessage(err.message || 'Không thể tải dữ liệu tiến độ học tập lúc này.');
        }
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [isAuthenticated]);

  const handleRetry = () => {
    setIsLoading(true);
    setErrorMessage(null);
    getProgressDashboard()
      .then((data) => setDashboardData(data))
      .catch((err: any) => setErrorMessage(err.message || 'Không thể tải dữ liệu tiến độ học tập lúc này.'))
      .finally(() => setIsLoading(false));
  };

  return (
    <PageShell className="space-y-8 pb-12">
      {/* Header */}
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.12),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="Student Learning Analytics • C# OOP"
            title="Bảng theo dõi tiến độ học tập C# OOP"
            description="Phân tích năng lực và sự tiến bộ dựa trên dữ liệu thực hành bài tập và mức độ tự chủ tư duy. Điểm số là ước lượng từ hệ thống (System Estimate) theo mô hình tất định minh bạch, không phải phép đo tâm lý tuyệt đối."
          />
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <Badge tone="rose">
              <GraduationCap className="h-3.5 w-3.5" aria-hidden="true" />
              Lộ trình C# OOP
            </Badge>
            <Badge tone="teal">
              <Cpu className="h-3.5 w-3.5" aria-hidden="true" />
              Ước lượng tất định
            </Badge>
          </div>
        </div>
      </section>

      {authLoading ? (
        <AuthLoadingState />
      ) : !isAuthenticated ? (
        <AuthRequiredState
          title="Đăng nhập để xem tiến độ học tập"
          description="Tiến độ các chủ đề C# OOP và lịch sử hoàn thành bài tập được lưu gắn liền với tài khoản của bạn."
        />
      ) : isLoading ? (
        <div className="flex min-h-[320px] flex-col items-center justify-center gap-3 rounded-[2rem] border border-slate-200 bg-white p-8 text-center shadow-sm">
          <Loader2 className="h-8 w-8 animate-spin text-rose-600" />
          <p className="text-sm font-semibold text-slate-700">Đang tổng hợp dữ liệu tiến độ từ các lần thử...</p>
        </div>
      ) : errorMessage ? (
        <div className="space-y-4">
          <ErrorAlert>
            <p className="font-semibold text-red-950">{errorMessage}</p>
          </ErrorAlert>
          <Button variant="secondary" size="md" onClick={handleRetry} className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Thử tải lại
          </Button>
        </div>
      ) : !dashboardData || dashboardData.is_empty || dashboardData.total_attempts_count === 0 ? (
        /* Empty State for New Users */
        <div className="rounded-[2rem] border-2 border-dashed border-rose-200 bg-white p-8 text-center shadow-sm sm:p-12 space-y-6">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-50 text-rose-600">
            <Sparkles className="h-8 w-8" />
          </div>
          <div className="max-w-xl mx-auto space-y-2">
            <h2 className="text-2xl font-bold text-slate-900">
              Chào mừng bạn đến với Lộ trình C# OOP!
            </h2>
            <p className="text-sm leading-relaxed text-slate-600">
              Bạn chưa thực hiện lần thử bài tập nào. Hệ thống đang áp dụng điểm khởi tạo trung tính{' '}
              <span className="font-mono font-bold text-slate-800">0.50 / 1.0 (Neutral Estimate)</span>{' '}
              cho toàn bộ 16 kỹ năng trong Taxonomy C# OOP. Điểm số sẽ tự động cập nhật trung thực khi bạn giải bài tập tại không gian gia sư.
            </p>
          </div>

          <div className="pt-2">
            <Link
              href="/tutor"
              className="inline-flex items-center gap-2 rounded-2xl bg-rose-600 px-6 py-3 text-sm font-bold text-white shadow-lg shadow-rose-200 transition hover:bg-rose-700"
            >
              <Code2 className="h-4 w-4" />
              Bắt đầu làm bài tập tại Gia sư C# OOP
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      ) : (
        /* Authenticated Dashboard Content */
        <div className="space-y-8">
          {/* Overview Metrics Cards */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {/* Metric 1: Practiced Skills */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Kỹ năng đã thực hành
                </span>
                <BookCheck className="h-5 w-5 text-indigo-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">
                {dashboardData.practiced_skills} / {dashboardData.total_skills}
              </p>
              <p className="mt-1 text-xs text-slate-500">Kỹ năng trong Taxonomy C# OOP</p>
            </div>

            {/* Metric 2: Current Mastery Estimate */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Ước tính thuần thục
                </span>
                <Cpu className="h-5 w-5 text-rose-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">
                {dashboardData.current_mastery_estimate.toFixed(2)} / 1.0
              </p>
              <div className="mt-1 flex items-center gap-1 text-[11px] text-rose-700 font-medium">
                <Info className="h-3 w-3 shrink-0" />
                <span>Ước tính từ hệ thống (System Estimate)</span>
              </div>
            </div>

            {/* Metric 3: Independent Solution Rate */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Tự chủ giải độc lập
                </span>
                <Sparkles className="h-5 w-5 text-teal-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">
                {dashboardData.independent_solution_rate !== null
                  ? `${Math.round(dashboardData.independent_solution_rate * 100)}%`
                  : 'Chưa có dữ liệu'}
              </p>
              <p className="mt-1 text-xs text-slate-500">
                {dashboardData.independent_success_count} bài thành công không cần gợi ý
              </p>
            </div>

            {/* Metric 4: Average Hint Level */}
            <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Cấp gợi ý trung bình
                </span>
                <Lightbulb className="h-5 w-5 text-amber-600" />
              </div>
              <p className="mt-2 font-mono text-3xl font-extrabold text-slate-900">
                {dashboardData.average_hint_level !== null
                  ? `Cấp ${dashboardData.average_hint_level.toFixed(1)} / 4`
                  : 'Chưa dùng gợi ý'}
              </p>
              <p className="mt-1 text-xs text-slate-500">Mức độ hỗ trợ trung bình khi gặp khó</p>
            </div>
          </div>

          {/* 2-Column: Strong Topics & Topics Needing Practice */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Strong Topics Card */}
            <Card
              title="Chủ đề vững vàng (Strong Topics)"
              description="Các kỹ năng bạn đã giải quyết độc lập tốt và duy trì điểm ước tính cao."
            >
              {dashboardData.strong_topics.length === 0 ? (
                <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 text-center text-xs text-slate-500">
                  Chưa có kỹ năng đạt ngưỡng vững vàng (&ge; 0.65). Hãy tiếp tục giải bài độc lập không cần gợi ý!
                </div>
              ) : (
                <div className="space-y-3">
                  {dashboardData.strong_topics.map((skill) => (
                    <div
                      key={skill.skill_id}
                      className="flex items-center justify-between rounded-xl border border-teal-100 bg-teal-50/40 p-3.5 transition hover:bg-teal-50"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="h-4 w-4 text-teal-600" />
                          <span className="text-sm font-bold text-slate-900">
                            {skill.skill_name || skill.skill_id}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">
                          Thành công: {skill.success_count} lần • Gợi ý: {skill.hint_count}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge tone="teal" className="font-mono text-xs">
                          {skill.mastery_score.toFixed(2)}
                        </Badge>
                        <Link
                          href={`/tutor?topic=${skill.skill_id}`}
                          className="rounded-lg bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 border border-slate-200 hover:text-teal-700"
                        >
                          Luyện tiếp
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>

            {/* Topics Needing Practice Card */}
            <Card
              title="Chủ đề cần luyện tập thêm (Topics Needing Practice)"
              description="Các kỹ năng từng gặp lỗi hoặc kỹ năng trọng tâm nên thực hành tiếp theo."
            >
              {dashboardData.topics_needing_practice.length === 0 ? (
                <div className="rounded-xl border border-slate-100 bg-slate-50 p-4 text-center text-xs text-slate-500">
                  Bạn đang làm chủ rất tốt các kỹ năng đã thực hành!
                </div>
              ) : (
                <div className="space-y-3">
                  {dashboardData.topics_needing_practice.slice(0, 5).map((skill) => (
                    <div
                      key={skill.skill_id}
                      className="flex items-center justify-between rounded-xl border border-amber-100 bg-amber-50/40 p-3.5 transition hover:bg-amber-50"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Target className="h-4 w-4 text-amber-600" />
                          <span className="text-sm font-bold text-slate-900">
                            {skill.skill_name || skill.skill_id}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500">
                          {skill.failure_count > 0
                            ? `Cần rà soát lại (${skill.failure_count} lần gặp khó)`
                            : 'Kỹ năng nền tảng nên luyện tập tiếp theo'}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge tone="amber" className="font-mono text-xs">
                          {skill.mastery_score.toFixed(2)}
                        </Badge>
                        <Link
                          href={`/tutor?topic=${skill.skill_id}`}
                          className="rounded-lg bg-white px-2.5 py-1 text-xs font-semibold text-slate-700 border border-slate-200 hover:text-amber-700"
                        >
                          Luyện ngay
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>

          {/* All OOP Skills Taxonomy Progress */}
          <Card
            title="Lộ trình toàn bộ 16 Kỹ năng C# OOP"
            description="Mức độ thuần thục ước lượng từ hệ thống cho từng khái niệm lập trình hướng đối tượng."
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {dashboardData.all_skills.map((skill) => {
                const isPracticed = skill.success_count + skill.failure_count > 0 || skill.last_practiced_at !== null;
                const percentage = Math.round(skill.mastery_score * 100);

                return (
                  <div
                    key={skill.skill_id}
                    className="rounded-2xl border border-slate-200 bg-white p-4 space-y-3 transition hover:border-slate-300 shadow-sm"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h3 className="text-sm font-bold text-slate-900">
                          {skill.skill_name || skill.skill_id}
                        </h3>
                        <span className="text-[11px] font-mono text-slate-500">{skill.skill_id}</span>
                      </div>
                      <Badge tone={isPracticed ? (skill.mastery_score >= 0.65 ? 'teal' : 'amber') : 'slate'}>
                        {isPracticed ? (skill.mastery_score >= 0.65 ? 'Vững vàng' : 'Đang học') : 'Chưa học'}
                      </Badge>
                    </div>

                    {/* Progress Bar */}
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-slate-600">
                        <span>Ước tính hệ thống:</span>
                        <span className="font-mono font-bold text-slate-800">
                          {skill.mastery_score.toFixed(2)} / 1.0 ({percentage}%)
                        </span>
                      </div>
                      <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-300 ${
                            !isPracticed
                              ? 'bg-slate-300'
                              : skill.mastery_score >= 0.65
                              ? 'bg-teal-500'
                              : skill.mastery_score < 0.5
                              ? 'bg-rose-500'
                              : 'bg-amber-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-100">
                      <span>Thành công: {skill.success_count}</span>
                      <span>Chưa đạt: {skill.failure_count}</span>
                      <span>Gợi ý: {skill.hint_count}</span>
                      <Link
                        href={`/tutor?topic=${skill.skill_id}`}
                        className="font-semibold text-rose-600 hover:text-rose-700 hover:underline"
                      >
                        Học ngay &rarr;
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Recent Attempts History */}
          <Card
            title="Lịch sử bài làm & lần thử gần nhất"
            description="Các lần thử giải bài C# OOP đã được hệ thống ghi nhận và phân tích."
          >
            {dashboardData.recent_attempts.length === 0 ? (
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-6 text-center text-xs text-slate-500">
                Chưa có lần thử làm bài nào được ghi nhận.
              </div>
            ) : (
              <div className="space-y-2.5">
                {dashboardData.recent_attempts.map((attempt) => {
                  const isSuccess = ['resolved', 'likely_resolved', 'completed', 'success'].includes(
                    attempt.outcome.toLowerCase()
                  );
                  const attemptDate = new Date(attempt.created_at).toLocaleString('vi-VN', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  });

                  return (
                    <div
                      key={attempt.attempt_id}
                      className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-white p-3.5 transition hover:border-slate-300 sm:flex-row sm:items-center sm:justify-between text-xs"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <Badge tone={isSuccess ? 'teal' : 'amber'}>
                            {isSuccess ? 'Đã giải quyết' : 'Cần hoàn thiện'}
                          </Badge>
                          <span className="font-semibold text-slate-900">{attempt.problem_title}</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-2 text-slate-500">
                          <span>{attemptDate}</span>
                          {attempt.skills.length > 0 && (
                            <>
                              <span>•</span>
                              <span>Kỹ năng: {attempt.skills.join(', ')}</span>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-3 text-slate-600 font-mono text-[11px] sm:text-right">
                        <span>Gợi ý: Cấp {attempt.highest_hint_level} / 4</span>
                        <span>({attempt.hints_used} lượt)</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </Card>
        </div>
      )}
    </PageShell>
  );
}
