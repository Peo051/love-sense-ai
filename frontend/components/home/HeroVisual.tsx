import { Code2, Cpu, Lightbulb, LockKeyhole, ShieldCheck } from 'lucide-react';

import Badge from '@/components/common/Badge';

const oopMetrics = [
  { label: 'Tính đóng gói (Encapsulation)', value: '95%', width: 'w-[95%]' },
  { label: 'Xử lý ngoại lệ (Exception Handling)', value: '85%', width: 'w-[85%]' },
  { label: 'Nguyên lý OOP sạch (Clean OOP)', value: '90%', width: 'w-[90%]' },
];

export default function HeroVisual() {
  return (
    <div className="landing-fade-up landing-fade-delay-1 w-full min-w-0">
      <div className="landing-preview-float relative mx-auto max-w-xl">
        <div className="pointer-events-none absolute -left-8 top-8 h-28 w-28 rounded-full bg-rose-300/35 blur-3xl" />
        <div className="pointer-events-none absolute -right-6 bottom-16 h-32 w-32 rounded-full bg-teal-300/24 blur-3xl" />
        <div className="pointer-events-none absolute left-1/2 top-1/2 h-44 w-44 -translate-x-1/2 -translate-y-1/2 rounded-full bg-rose-200/35 blur-3xl" />

        <div className="relative overflow-hidden rounded-[2rem] border-2 border-slate-900 bg-white p-4 shadow-[9px_9px_0_rgba(31,41,55,0.14)] ring-1 ring-white/80 backdrop-blur">
          <div className="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-rose-300/70 to-transparent" />
          <div className="absolute inset-x-0 top-0 h-20 bg-gradient-to-b from-rose-50/80 to-transparent" />

          <div className="relative mb-4 flex flex-col gap-3 min-[430px]:flex-row min-[430px]:items-center min-[430px]:justify-between">
            <div className="min-w-0">
              <p className="text-sm font-black text-slate-950">Gia sư C# OOP Demo</p>
              <p className="text-xs text-slate-500">Phân tích code thích ứng & gợi ý tư duy</p>
            </div>
            <Badge tone="teal" className="max-w-full shrink-0 whitespace-normal text-left">
              <LockKeyhole className="h-3.5 w-3.5" aria-hidden="true" />
              Bảo mật mã nguồn học viên
            </Badge>
          </div>

          <div className="relative grid gap-4">
            <div className="rounded-2xl border border-slate-200 bg-slate-950 p-4 font-mono text-xs text-slate-200 shadow-sm">
              <div className="mb-2 flex items-center justify-between border-b border-slate-800 pb-2">
                <span className="flex items-center gap-1.5 text-rose-400 font-bold">
                  <Code2 className="h-3.5 w-3.5" />
                  BankAccount.cs
                </span>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">C# 12 / .NET 8</span>
              </div>
              <pre className="overflow-x-auto leading-relaxed text-slate-300">
                <code>
                  <span className="text-purple-400">public class</span> <span className="text-yellow-300">BankAccount</span> {'{\n'}
                  {'  '}<span className="text-purple-400">private decimal</span> _balance;{'\n\n'}
                  {'  '}<span className="text-purple-400">public void</span> <span className="text-blue-400">Withdraw</span>(<span className="text-purple-400">decimal</span> amount) {'{\n'}
                  {'    '}<span className="text-purple-400">if</span> (amount &lt;= 0 || amount &gt; _balance){'\n'}
                  {'      '}<span className="text-purple-400">throw new</span> <span className="text-yellow-300">InvalidOperationException</span>();{'\n'}
                  {'    '}_balance -= amount;{'\n'}
                  {'  }'}{'\n'}
                  {'}'}
                </code>
              </pre>
            </div>

            <div className="rounded-2xl border border-rose-200 bg-white p-4 shadow-sm shadow-rose-100">
              <div className="mb-3 flex items-start justify-between gap-3">
                <div>
                  <p className="font-mono text-xs font-bold uppercase tracking-[0.16em] text-rose-600">Socratic Diagnosis</p>
                  <p className="mt-1 break-words text-base font-bold text-slate-950">Phân tích tính đóng gói (Encapsulation)</p>
                </div>
                <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-rose-200 bg-rose-100 text-rose-600">
                  <Cpu className="h-4 w-4" aria-hidden="true" />
                </span>
              </div>

              <div className="space-y-2.5">
                {oopMetrics.map((bar) => (
                  <div key={bar.label}>
                    <div className="mb-1 flex justify-between text-xs font-medium text-slate-600">
                      <span>{bar.label}</span>
                      <span className="font-mono font-bold text-slate-900">{bar.value}</span>
                    </div>
                    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
                      <div className={`h-full rounded-full bg-gradient-to-r from-rose-500 to-teal-500 ${bar.width}`} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-teal-200 bg-teal-50/90 p-4 shadow-sm">
              <div className="flex gap-3">
                <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl border border-teal-200 bg-white text-teal-700">
                  <Lightbulb className="h-4 w-4" aria-hidden="true" />
                </span>
                <div>
                  <p className="font-mono text-xs font-bold uppercase tracking-[0.16em] text-teal-800">Gợi ý tư duy từng bước</p>
                  <p className="mt-1 text-xs leading-5 text-slate-700">
                    “Thuộc tính <code className="rounded bg-teal-100/70 px-1 py-0.5 font-mono text-teal-900">_balance</code> đã được bảo vệ đúng cách bằng access modifier <code className="rounded bg-teal-100/70 px-1 py-0.5 font-mono text-teal-900">private</code>. Hãy suy nghĩ thêm: lớp con kế thừa có cần truy xuất số dư không và bạn nên dùng <code className="rounded bg-teal-100/70 px-1 py-0.5 font-mono text-teal-900">protected</code> hay Property public?”
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-4 py-2.5 text-xs font-bold text-slate-700 shadow-sm">
              <ShieldCheck className="h-4 w-4 text-emerald-600" aria-hidden="true" />
              Hướng dẫn gợi mở tư duy, không giải hộ đáp án hoàn chỉnh.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
