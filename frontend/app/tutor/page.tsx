'use client';

import { useState } from 'react';
import {
  AlertCircle,
  BookOpen,
  Code2,
  Cpu,
  FileCode2,
  Info,
  Lightbulb,
  Sparkles,
  Terminal,
} from 'lucide-react';

import { InfoAlert, WarningAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import type { OcrExtractionResult } from '@/lib/ocr';
import { textareaClassName } from '@/lib/ui';

const oopTopics = [
  'Lớp và Đối tượng (Classes & Objects)',
  'Tính đóng gói (Encapsulation)',
  'Tính kế thừa (Inheritance)',
  'Tính đa hình (Polymorphism)',
  'Lớp trừu tượng & Interface (Abstraction & Interfaces)',
  'Xử lý ngoại lệ (Exception Handling)',
];

export default function TutorPage() {
  const [codeText, setCodeText] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(oopTopics[0]);
  const [exerciseGoal, setExerciseGoal] = useState('');
  const [activeTab, setActiveTab] = useState<'editor' | 'ocr'>('editor');

  const handleTextExtracted = (extractedText: string, _result: OcrExtractionResult, mode: 'replace' | 'append') => {
    setCodeText((current) => (mode === 'append' && current ? `${current}\n\n${extractedText}` : extractedText));
    setActiveTab('editor');
  };

  return (
    <PageShell className="space-y-8 pb-12">
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.12),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="Adaptive Programming Tutor"
            title="Gia sư lập trình C# OOP"
            description="Không gian thực hành và nhận gợi ý tư duy lập trình hướng đối tượng từng bước. Phân tích mã nguồn, chỉ ra nguyên nhân lỗi và hướng dẫn tư duy độc lập."
          />
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <Badge tone="rose">
              <Code2 className="h-3.5 w-3.5" aria-hidden="true" />
              C# / .NET OOP
            </Badge>
            <Badge tone="teal">
              <Cpu className="h-3.5 w-3.5" aria-hidden="true" />
              Socratic Guidance
            </Badge>
          </div>
        </div>
      </section>

      {/* Migration in progress notice */}
      <WarningAlert>
        <div className="flex flex-col gap-1">
          <strong className="font-bold">Hệ thống đang nâng cấp backend (Tutor Backend Migration In Progress)</strong>
          <span>
            Backend phân tích code và engine gợi mở Socratic C# OOP đang được kết nối trong các bước kế tiếp.
            Hiện tại bạn có thể xem trước giao diện, nhập code hoặc sử dụng công cụ OCR trích xuất mã nguồn từ ảnh chụp màn hình bài tập.
          </span>
        </div>
      </WarningAlert>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(380px,0.85fr)] lg:items-start">
        {/* Left Column: Code Workspace / OCR */}
        <div className="space-y-6">
          <Card
            title="Không gian bài tập"
            description="Nhập mã nguồn C# của bạn hoặc chuyển sang tab OCR để quét code từ ảnh chụp bài tập."
          >
            <div className="mb-4 flex gap-2 border-b border-slate-200 pb-3">
              <button
                type="button"
                onClick={() => setActiveTab('editor')}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-bold transition ${
                  activeTab === 'editor'
                    ? 'border border-rose-200 bg-rose-50 text-rose-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <FileCode2 className="h-4 w-4" />
                Mã nguồn C#
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('ocr')}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-bold transition ${
                  activeTab === 'ocr'
                    ? 'border border-rose-200 bg-rose-50 text-rose-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Terminal className="h-4 w-4" />
                Quét từ ảnh chụp bài tập (OCR)
              </button>
            </div>

            {activeTab === 'editor' ? (
              <div className="space-y-4">
                <FieldLabel
                  htmlFor="topic-select"
                  label="Chủ đề OOP"
                  hint="Chọn chủ đề kiến thức liên quan đến đoạn mã cần hỗ trợ."
                >
                  <select
                    id="topic-select"
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-4 focus:ring-rose-100"
                  >
                    {oopTopics.map((topic) => (
                      <option key={topic} value={topic}>
                        {topic}
                      </option>
                    ))}
                  </select>
                </FieldLabel>

                <FieldLabel
                  htmlFor="exercise-goal"
                  label="Yêu cầu bài tập hoặc lỗi đang gặp"
                  hint="Ví dụ: 'Phương thức Withdraw chưa kiểm tra số dư' hoặc 'Lỗi CS0122: inaccessible due to its protection level'"
                >
                  <input
                    id="exercise-goal"
                    type="text"
                    value={exerciseGoal}
                    onChange={(e) => setExerciseGoal(e.target.value)}
                    placeholder="Nhập mô tả lỗi hoặc mục tiêu cần đạt được..."
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-4 focus:ring-rose-100"
                  />
                </FieldLabel>

                <FieldLabel
                  htmlFor="code-input"
                  label="Mã nguồn C#"
                  hint="Dán code class, method hoặc đoạn mã bạn đang viết."
                >
                  <textarea
                    id="code-input"
                    rows={12}
                    value={codeText}
                    onChange={(e) => setCodeText(e.target.value)}
                    placeholder={`// Dán mã nguồn C# OOP tại đây...\npublic class Student {\n    private string _name;\n    public Student(string name) {\n        _name = name;\n    }\n}`}
                    className={`${textareaClassName} font-mono text-sm leading-relaxed`}
                  />
                </FieldLabel>

                <Button
                  type="button"
                  size="lg"
                  className="w-full"
                  disabled={!codeText.trim()}
                  onClick={() => alert('Gia sư backend đang trong quá trình chuyển đổi (Migration In Progress).')}
                >
                  <Sparkles className="h-4 w-4" />
                  Gửi mã nguồn đến Gia sư AI
                </Button>
              </div>
            ) : (
              <ImageOcrUploader
                hasChatText={Boolean(codeText.trim())}
                onTextExtracted={handleTextExtracted}
                title="Quét mã nguồn từ ảnh bài tập (OCR)"
                description="Tải ảnh chụp màn hình bài tập C#, đề bài hoặc lỗi compiler để trích xuất mã nguồn vào trình soạn thảo."
                uploadLabel="Tải ảnh chụp màn hình bài tập"
              />
            )}
          </Card>
        </div>

        {/* Right Column: Tutor Preview & Guidance Rules */}
        <div className="space-y-6">
          <Card
            title="Nguyên tắc gia sư thích ứng"
            description="Cách CodeSense AI giúp bạn rèn luyện tư duy lập trình C# OOP."
          >
            <div className="space-y-4 text-sm text-slate-700">
              <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-rose-50/70 p-3.5">
                <Lightbulb className="h-5 w-5 shrink-0 text-rose-600 mt-0.5" />
                <div>
                  <p className="font-bold text-slate-900">Gợi mở từng bước (Socratic Method)</p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Gia sư chỉ ra mấu chốt vấn đề và đặt câu hỏi gợi mở, giúp bạn tự tư duy thay vì chỉ copy code giải sẵn.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
                <BookOpen className="h-5 w-5 shrink-0 text-teal-600 mt-0.5" />
                <div>
                  <p className="font-bold text-slate-900">Chuẩn hóa nguyên lý C# OOP</p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Nhấn mạnh các quy tắc: access modifiers (private, protected, public), tính bao đóng của dữ liệu, và cách tổ chức quan hệ giữa các lớp.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
                <Terminal className="h-5 w-5 shrink-0 text-slate-700 mt-0.5" />
                <div>
                  <p className="font-bold text-slate-900">Phát hiện lỗi thường gặp</p>
                  <p className="mt-1 text-xs leading-5 text-slate-600">
                    Cảnh báo NullReferenceException, lỗi phạm vi truy xuất, lỗi thiếu constructor khởi tạo hoặc nhầm lẫn giữa Override và New method.
                  </p>
                </div>
              </div>
            </div>
          </Card>

          <Card title="Gợi ý mẫu khi hoàn tất di chuyển">
            <div className="rounded-2xl border border-teal-200 bg-teal-50/80 p-4 text-xs font-mono leading-relaxed text-teal-950">
              <p className="font-bold text-teal-800">[Gia sư CodeSense AI - Level 1 Hint]</p>
              <p className="mt-2 text-slate-700 font-sans">
                Quan sát thuộc tính <code className="font-mono font-bold text-teal-900">_balance</code> của bạn: hiện tại phương thức <code className="font-mono font-bold text-teal-900">Withdraw</code> chưa kiểm tra trường hợp số tiền rút lớn hơn số dư hiện có. Hãy thêm câu lệnh điều kiện để bảo toàn dữ liệu.
              </p>
            </div>
          </Card>
        </div>
      </div>
    </PageShell>
  );
}
