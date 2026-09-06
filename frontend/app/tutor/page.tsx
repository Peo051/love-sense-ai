'use client';

import { useState } from 'react';
import {
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  Code2,
  Cpu,
  FileCode2,
  HelpCircle,
  Info,
  Lightbulb,
  Loader2,
  RefreshCw,
  Sparkles,
  Terminal,
} from 'lucide-react';

import { ErrorAlert, InfoAlert, SuccessAlert, WarningAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import { analyzeTutorCode, requestTutorNextHint, verifyTutorRetry } from '@/lib/api';
import type { OcrExtractionResult } from '@/lib/ocr';
import type {
  TutorDiagnosisCategory,
  TutorResponse,
  TutorVerifyResponse,
  VerificationStatus,
} from '@/lib/types';
import { textareaClassName } from '@/lib/ui';

const oopTopics = [
  { code: 'csharp.class_object', label: 'Lớp và Đối tượng (Classes & Objects)' },
  { code: 'csharp.property', label: 'Thuộc tính & Đóng gói (Properties & Encapsulation)' },
  { code: 'csharp.constructor', label: 'Hàm khởi tạo (Constructors)' },
  { code: 'csharp.this', label: 'Từ khóa this & Shadowing' },
  { code: 'csharp.method', label: 'Phương thức & Hành vi (Methods)' },
  { code: 'csharp.encapsulation', label: 'Tính bao đóng & Access Modifiers' },
  { code: 'csharp.validation', label: 'Ràng buộc dữ liệu & Setter (Validation)' },
  { code: 'csharp.static', label: 'Thành viên tĩnh (Static vs Instance)' },
  { code: 'csharp.inheritance', label: 'Tính kế thừa (Inheritance)' },
  { code: 'csharp.override', label: 'Ghi đè phương thức (Override & Virtual)' },
  { code: 'csharp.polymorphism', label: 'Tính đa hình (Polymorphism)' },
];

const categoryLabels: Record<TutorDiagnosisCategory, string> = {
  compile_error: 'Lỗi biên dịch cú pháp / kiểu dữ liệu',
  runtime_error: 'Nguy cơ lỗi thời gian chạy (Runtime)',
  logic_error: 'Sai lệch logic xử lý hoặc trạng thái',
  conceptual_misuse: 'Nhầm lẫn khái niệm OOP',
  requirement_violation: 'Chưa đáp ứng đúng yêu cầu bài tập',
  no_bug: 'Mã nguồn chuẩn xác, không có lỗi',
  insufficient_context: 'Mã nguồn quá ngắn, cần bổ sung ngữ cảnh',
  unknown: 'Vấn đề kỹ thuật cần kiểm tra thêm',
};

const hintLevelNames = [
  'Level 1: Gợi mở Socratic',
  'Level 2: Giải thích khái niệm',
  'Level 3: Chỉ vị trí & hướng sửa',
  'Level 4: Hướng dẫn sửa cụ thể',
];

function getCalibratedConfidence(confidence: number): {
  label: string;
  tone: 'teal' | 'amber' | 'slate';
  icon: any;
  description: string;
} {
  if (confidence >= 0.8) {
    return {
      label: 'Phát hiện có căn cứ rõ ràng',
      tone: 'teal',
      icon: CheckCircle2,
      description: 'Chẩn đoán có bằng chứng cụ thể trong đoạn mã nguồn bạn nộp.',
    };
  }
  if (confidence >= 0.5) {
    return {
      label: 'Giả thuyết định hướng cần lưu ý',
      tone: 'amber',
      icon: AlertCircle,
      description: 'Chẩn đoán định hướng để bạn tự rà soát, không khẳng định tuyệt đối.',
    };
  }
  return {
    label: 'Dấu hiệu chưa chắc chắn',
    tone: 'slate',
    icon: Info,
    description: 'Bằng chứng đoạn mã chưa rõ ràng, phản hồi mang tính chất gợi ý bước đầu.',
  };
}

export default function TutorPage() {
  const [problemStatement, setProblemStatement] = useState('');
  const [studentCode, setStudentCode] = useState('');
  const [compilerError, setCompilerError] = useState('');
  const [studentQuestion, setStudentQuestion] = useState('');
  const [selectedTopic, setSelectedTopic] = useState(oopTopics[0].code);
  const [activeTab, setActiveTab] = useState<'editor' | 'ocr'>('editor');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingHint, setIsLoadingHint] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [tutorResult, setTutorResult] = useState<TutorResponse | null>(null);
  const [currentHintLevel, setCurrentHintLevel] = useState(1);
  const [highestHintLevel, setHighestHintLevel] = useState(1);
  const [solutionRevealed, setSolutionRevealed] = useState(false);
  const [hintHistory, setHintHistory] = useState<Array<{ level: number; text: string }>>([]);

  const [revisedCode, setRevisedCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<TutorVerifyResponse | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  const handleTextExtracted = (extractedText: string, _result: OcrExtractionResult, mode: 'replace' | 'append') => {
    setStudentCode((current) => (mode === 'append' && current ? `${current}\n\n${extractedText}` : extractedText));
    setActiveTab('editor');
  };

  const handleCodeKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const val = textarea.value;
      const nextVal = val.substring(0, start) + '    ' + val.substring(end);
      setStudentCode(nextVal);
      requestAnimationFrame(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      });
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!problemStatement.trim() || !studentCode.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setErrorMessage(null);
    setVerifyResult(null);
    setVerifyError(null);

    try {
      const response = await analyzeTutorCode({
        problem_statement: problemStatement.trim(),
        student_code: studentCode.trim(),
        programming_language: 'csharp',
        compiler_error: compilerError.trim() ? compilerError.trim() : null,
        student_question: studentQuestion.trim() ? studentQuestion.trim() : null,
        topic: selectedTopic,
        hint_level: 1,
        save_input: false,
        save_result: true,
      });

      setTutorResult(response);
      setCurrentHintLevel(response.hint_level || 1);
      setHighestHintLevel(response.highest_hint_level_used || response.hint_level || 1);
      setSolutionRevealed(Boolean(response.solution_revealed));
      setHintHistory([{ level: response.hint_level || 1, text: response.tutor_response }]);
      setRevisedCode(studentCode);
    } catch (err: any) {
      setErrorMessage(err.message || 'Đã xảy ra sự cố khi phân tích mã nguồn. Vui lòng thử lại.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNextHint = async () => {
    if (!tutorResult || currentHintLevel >= 4 || isLoadingHint) return;

    setIsLoadingHint(true);
    setErrorMessage(null);

    try {
      const nextHintRes = await requestTutorNextHint({
        session_id: tutorResult.session_id,
        guest_context_token: tutorResult.guest_context_token,
        current_hint_level: currentHintLevel,
        current_diagnosis: tutorResult.diagnosis,
        student_code: studentCode,
      });

      setCurrentHintLevel(nextHintRes.hint_level);
      setHighestHintLevel(nextHintRes.highest_hint_level_used);
      setSolutionRevealed(nextHintRes.solution_revealed);
      setTutorResult((prev) =>
        prev
          ? {
              ...prev,
              hint_level: nextHintRes.hint_level,
              highest_hint_level_used: nextHintRes.highest_hint_level_used,
              tutor_response: nextHintRes.tutor_response,
              solution_revealed: nextHintRes.solution_revealed,
              next_action: nextHintRes.next_action,
              teaching_strategy: nextHintRes.teaching_strategy,
              guest_context_token: nextHintRes.guest_context_token || prev.guest_context_token,
            }
          : null
      );
      setHintHistory((prev) => [
        ...prev,
        { level: nextHintRes.hint_level, text: nextHintRes.tutor_response },
      ]);
    } catch (err: any) {
      setErrorMessage(err.message || 'Không thể lấy gợi ý tiếp theo lúc này. Vui lòng thử lại.');
    } finally {
      setIsLoadingHint(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!revisedCode.trim() || isVerifying || !tutorResult) return;

    setIsVerifying(true);
    setVerifyError(null);

    try {
      const res = await verifyTutorRetry({
        original_problem: problemStatement,
        revised_student_code: revisedCode.trim(),
        previous_code: studentCode,
        original_diagnosis: tutorResult.diagnosis,
        session_id: tutorResult.session_id,
        guest_context_token: tutorResult.guest_context_token,
      });
      setVerifyResult(res);
    } catch (err: any) {
      setVerifyError(err.message || 'Không thể xác minh bài sửa lúc này. Vui lòng thử lại.');
    } finally {
      setIsVerifying(false);
    }
  };

  const confidenceInfo = tutorResult ? getCalibratedConfidence(tutorResult.diagnosis.confidence) : null;

  return (
    <PageShell className="space-y-8 pb-12">
      {/* Header */}
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.12),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="CodeSense AI Tutor"
            title="Không gian Gia Sư Lập Trình C# OOP"
            description="Học lập trình hướng đối tượng thích ứng qua phương pháp gợi mở Socratic. Phân tích nguyên nhân lỗi, dẫn dắt tư duy từng bước và xác minh bài sửa mà không tiết lộ đáp án sớm."
          />
          <div className="flex flex-wrap gap-2 lg:justify-end">
            <Badge tone="rose">
              <Code2 className="h-3.5 w-3.5" aria-hidden="true" />
              C# / .NET OOP
            </Badge>
            <Badge tone="teal">
              <Cpu className="h-3.5 w-3.5" aria-hidden="true" />
              Socratic Progressive Hints
            </Badge>
          </div>
        </div>
      </section>

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(380px,0.85fr)] lg:items-start">
        {/* Left Column: Input Form & Code Editor */}
        <div className="space-y-6">
          <Card
            title="Bài tập & Mã nguồn C#"
            description="Nhập đề bài và đoạn mã của bạn để nhận chẩn đoán sư phạm và gợi ý tư duy tự sửa lỗi."
          >
            <div className="mb-5 flex gap-2 border-b border-slate-200 pb-3">
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
                Trình soạn thảo mã nguồn
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
              <form onSubmit={handleAnalyze} className="space-y-5">
                <FieldLabel
                  htmlFor="topic-select"
                  label="Chủ đề kiến thức OOP"
                  hint="Giúp gia sư định hình trọng tâm khái niệm đang học."
                >
                  <select
                    id="topic-select"
                    value={selectedTopic}
                    onChange={(e) => setSelectedTopic(e.target.value)}
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-4 focus:ring-rose-100"
                  >
                    {oopTopics.map((t) => (
                      <option key={t.code} value={t.code}>
                        {t.label}
                      </option>
                    ))}
                  </select>
                </FieldLabel>

                <FieldLabel
                  htmlFor="problem-statement-input"
                  label="Đề bài bài tập"
                  hint="Mô tả yêu cầu cần giải quyết của bài toán lập trình."
                >
                  <textarea
                    id="problem-statement-input"
                    rows={3}
                    value={problemStatement}
                    onChange={(e) => setProblemStatement(e.target.value)}
                    placeholder="Ví dụ: Tạo lớp BankAccount có trường số dư private và thuộc tính Balance chỉ đọc. Phương thức Withdraw cần kiểm tra số dư đủ trước khi rút..."
                    className={textareaClassName}
                  />
                </FieldLabel>

                <FieldLabel
                  htmlFor="student-code-input"
                  label="Mã nguồn C# của bạn"
                  hint="Nhập hoặc dán đoạn mã lớp hoặc phương thức. Hỗ trợ phím Tab để thụt dòng."
                >
                  <textarea
                    id="student-code-input"
                    rows={11}
                    value={studentCode}
                    onChange={(e) => setStudentCode(e.target.value)}
                    onKeyDown={handleCodeKeyDown}
                    placeholder={`// Dán mã nguồn C# của bạn tại đây...\npublic class BankAccount {\n    private decimal _balance;\n\n    public decimal Balance {\n        get { return _balance; }\n    }\n}`}
                    className={`${textareaClassName} font-mono text-sm leading-relaxed`}
                  />
                </FieldLabel>

                <FieldLabel
                  htmlFor="compiler-error-input"
                  label="Thông báo lỗi biên dịch (Compiler Error - tùy chọn)"
                  hint="Dán mã lỗi từ Visual Studio hoặc terminal nếu có (ví dụ: CS0103, CS0169...)"
                >
                  <input
                    id="compiler-error-input"
                    type="text"
                    value={compilerError}
                    onChange={(e) => setCompilerError(e.target.value)}
                    placeholder="Ví dụ: CS0122: 'BankAccount._balance' is inaccessible due to its protection level"
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-2 text-sm font-mono text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-4 focus:ring-rose-100"
                  />
                </FieldLabel>

                <FieldLabel
                  htmlFor="student-question-input"
                  label="Câu hỏi / Băn khoăn của bạn (tùy chọn)"
                  hint="Nêu điều bạn chưa rõ để gia sư giải thích kỹ hơn theo đúng trọng tâm."
                >
                  <input
                    id="student-question-input"
                    type="text"
                    value={studentQuestion}
                    onChange={(e) => setStudentQuestion(e.target.value)}
                    placeholder="Ví dụ: Em muốn hỏi cách gán giá trị cho trường private qua constructor..."
                    className="w-full rounded-2xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-4 focus:ring-rose-100"
                  />
                </FieldLabel>

                {errorMessage && (
                  <ErrorAlert>
                    <p className="font-semibold text-red-950">{errorMessage}</p>
                  </ErrorAlert>
                )}

                <Button
                  type="submit"
                  size="lg"
                  className="w-full"
                  disabled={!problemStatement.trim() || !studentCode.trim() || isAnalyzing}
                  isLoading={isAnalyzing}
                >
                  <Sparkles className="h-4 w-4" />
                  {isAnalyzing ? 'Đang phân tích tư duy lập trình...' : 'Phân tích mã nguồn & Nhận gợi ý'}
                </Button>
              </form>
            ) : (
              <ImageOcrUploader
                hasChatText={Boolean(studentCode.trim())}
                onTextExtracted={handleTextExtracted}
                title="Quét mã nguồn từ ảnh bài tập (OCR)"
                description="Tải ảnh chụp bài tập C# hoặc ảnh lỗi màn hình để trích xuất văn bản vào trình soạn thảo."
                uploadLabel="Tải ảnh chụp bài tập"
              />
            )}
          </Card>
        </div>

        {/* Right Column: Pedagogical Result Area */}
        <div className="space-y-6">
          {!tutorResult ? (
            <div className="space-y-6">
              <Card
                title="Tiến trình gợi ý Socratic 4 cấp độ"
                description="CodeSense AI không giải bài hộ mà giúp bạn tự khám phá ra giải pháp."
              >
                <div className="space-y-3 text-sm text-slate-700">
                  <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-rose-50/70 p-3.5">
                    <Lightbulb className="h-5 w-5 shrink-0 text-rose-600 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-900">Level 1: Câu hỏi gợi mở Socratic</p>
                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Đặt câu hỏi kích thích tư duy, chỉ ra mấu chốt nguyên lý mà không tiết lộ vị trí sửa.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
                    <BookOpen className="h-5 w-5 shrink-0 text-teal-600 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-900">Level 2: Giải thích khái niệm OOP</p>
                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Nhắc lại kiến thức lý thuyết nền tảng (Encapsulation, Constructor, Getter/Setter).
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
                    <Terminal className="h-5 w-5 shrink-0 text-slate-700 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-900">Level 3: Chỉ dẫn vị trí & hướng sửa</p>
                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Khoanh vùng dòng lệnh có vấn đề và đưa ra hướng điều chỉnh từng bước.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-3.5">
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-amber-600 mt-0.5" />
                    <div>
                      <p className="font-bold text-slate-900">Level 4: Lời giải chi tiết & mã mẫu</p>
                      <p className="mt-1 text-xs leading-5 text-slate-600">
                        Chỉ hiển thị khi bạn đã vượt qua các cấp độ trước hoặc cần tham khảo lời giải đối chiếu.
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Card Diagnosis & Result */}
              <Card
                title="Chẩn đoán sư phạm"
                description="Đánh giá kỹ thuật và bằng chứng đoạn mã từ bài làm của bạn."
              >
                <div className="space-y-5">
                  {/* Calibrated Confidence Badge */}
                  {confidenceInfo && (
                    <div className="flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                      <div className="flex items-center gap-2">
                        <confidenceInfo.icon className={`h-4 w-4 ${
                          confidenceInfo.tone === 'teal'
                            ? 'text-teal-600'
                            : confidenceInfo.tone === 'amber'
                            ? 'text-amber-600'
                            : 'text-slate-600'
                        }`} />
                        <span className="text-xs font-semibold text-slate-800">
                          {confidenceInfo.label}
                        </span>
                      </div>
                      <Badge tone={confidenceInfo.tone}>
                        {tutorResult.diagnosis.severity.toUpperCase()}
                      </Badge>
                    </div>
                  )}

                  {/* Category & Issue Type */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                        Phân loại vấn đề
                      </span>
                      {tutorResult.diagnosis.location && (
                        <span className="text-xs font-mono text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full">
                          Vị trí: {tutorResult.diagnosis.location}
                        </span>
                      )}
                    </div>
                    <p className="text-base font-bold text-slate-900">
                      {categoryLabels[tutorResult.diagnosis.category] || tutorResult.diagnosis.issue_type}
                    </p>
                  </div>

                  {/* Knowledge Components */}
                  {tutorResult.knowledge_components && tutorResult.knowledge_components.length > 0 && (
                    <div className="space-y-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                        Khái niệm OOP liên quan
                      </span>
                      <div className="flex flex-wrap gap-2">
                        {tutorResult.knowledge_components.map((kc) => (
                          <Badge key={kc} tone="teal">
                            {kc}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Code Evidence */}
                  {tutorResult.evidence && (
                    <div className="space-y-2">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                        Bằng chứng đoạn mã liên quan
                      </span>
                      <div className="rounded-2xl border border-slate-200 bg-slate-900 p-3.5 text-xs font-mono text-slate-100 overflow-x-auto">
                        <pre className="whitespace-pre-wrap">{tutorResult.evidence.code}</pre>
                      </div>
                      <p className="text-xs text-slate-600 leading-relaxed italic">
                        {tutorResult.evidence.reason}
                      </p>
                    </div>
                  )}

                  {/* Misconception Hypothesis */}
                  {tutorResult.possible_misconception && (
                    <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50/70 p-3.5">
                      <AlertCircle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
                      <div className="text-xs">
                        <p className="font-bold text-amber-950">Gợi ý ngộ nhận tiềm ẩn:</p>
                        <p className="mt-0.5 text-amber-900 leading-relaxed">
                          {tutorResult.possible_misconception.description}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Tutor Response */}
                  <div className="rounded-2xl border-2 border-rose-200 bg-rose-50/70 p-4 space-y-3">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-rose-600" />
                      <h3 className="font-bold text-slate-900">
                        Lời khuyên của Gia sư AI ({hintLevelNames[currentHintLevel - 1]})
                      </h3>
                    </div>
                    <div className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
                      {tutorResult.tutor_response}
                    </div>
                    {tutorResult.next_action && (
                      <div className="flex items-center gap-2 rounded-xl bg-white/80 p-2.5 text-xs font-medium text-slate-700 border border-rose-100">
                        <ArrowRight className="h-3.5 w-3.5 text-rose-600 shrink-0" />
                        <span>Bước tiếp theo: {tutorResult.next_action}</span>
                      </div>
                    )}
                  </div>

                  {/* Hint Level Indicator & Next Hint Button */}
                  <div className="space-y-3 border-t border-slate-200 pt-4">
                    <div className="flex items-center justify-between text-xs text-slate-600">
                      <span>Cấp độ gợi ý hiện tại:</span>
                      <span className="font-bold text-rose-700">
                        Cấp {currentHintLevel} / 4 {solutionRevealed ? '(Đã hiện mã giải)' : ''}
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-1.5">
                      {[1, 2, 3, 4].map((lvl) => (
                        <div
                          key={lvl}
                          className={`h-2 rounded-full transition-all ${
                            lvl <= currentHintLevel
                              ? 'bg-rose-500'
                              : lvl <= highestHintLevel
                              ? 'bg-rose-200'
                              : 'bg-slate-200'
                          }`}
                        />
                      ))}
                    </div>

                    {currentHintLevel < 4 && !solutionRevealed && (
                      <Button
                        type="button"
                        variant="secondary"
                        size="md"
                        className="w-full"
                        onClick={handleNextHint}
                        isLoading={isLoadingHint}
                      >
                        <ChevronRight className="h-4 w-4" />
                        Yêu cầu gợi ý tiếp theo ({hintLevelNames[currentHintLevel]})
                      </Button>
                    )}
                  </div>
                </div>
              </Card>

              {/* Card Retry & Verify Area */}
              <Card
                title="Sửa lại & Xác minh (Retry & Verify)"
                description="Áp dụng gợi ý để chỉnh sửa mã nguồn và gửi yêu cầu xác minh trực tiếp."
              >
                <form onSubmit={handleVerify} className="space-y-4">
                  <FieldLabel
                    htmlFor="revised-code-input"
                    label="Mã nguồn sau khi sửa đổi"
                    hint="Chỉnh sửa lại đoạn code dựa trên các câu hỏi gợi mở phía trên."
                  >
                    <textarea
                      id="revised-code-input"
                      rows={8}
                      value={revisedCode}
                      onChange={(e) => setRevisedCode(e.target.value)}
                      className={`${textareaClassName} font-mono text-sm leading-relaxed`}
                      placeholder="// Nhập code C# đã chỉnh sửa..."
                    />
                  </FieldLabel>

                  {verifyError && (
                    <ErrorAlert>
                      <p className="font-semibold text-red-950">{verifyError}</p>
                    </ErrorAlert>
                  )}

                  <Button
                    type="submit"
                    variant="secondary"
                    size="md"
                    className="w-full"
                    disabled={!revisedCode.trim() || isVerifying}
                    isLoading={isVerifying}
                  >
                    <RefreshCw className="h-4 w-4" />
                    {isVerifying ? 'Đang xác minh bài sửa...' : 'Xác minh lần thử lại'}
                  </Button>

                  {/* Verification Result Display */}
                  {verifyResult && (
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                          Kết quả xác minh
                        </span>
                        <Badge
                          tone={
                            verifyResult.status === 'likely_resolved'
                              ? 'teal'
                              : verifyResult.status === 'still_present'
                              ? 'amber'
                              : verifyResult.status === 'new_issue'
                              ? 'rose'
                              : 'slate'
                          }
                        >
                          {verifyResult.status}
                        </Badge>
                      </div>

                      <p className="text-sm font-semibold text-slate-900">
                        {verifyResult.feedback}
                      </p>

                      {verifyResult.remaining_issues && verifyResult.remaining_issues.length > 0 && (
                        <div className="text-xs text-amber-900 bg-amber-50 p-2.5 rounded-xl border border-amber-200">
                          <p className="font-bold">Vấn đề cần sửa tiếp:</p>
                          <ul className="list-disc pl-4 mt-1 space-y-0.5">
                            {verifyResult.remaining_issues.map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {verifyResult.new_issues && verifyResult.new_issues.length > 0 && (
                        <div className="text-xs text-red-900 bg-red-50 p-2.5 rounded-xl border border-red-200">
                          <p className="font-bold">Vấn đề mới phát sinh:</p>
                          <ul className="list-disc pl-4 mt-1 space-y-0.5">
                            {verifyResult.new_issues.map((issue, idx) => (
                              <li key={idx}>{issue}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      <div className="text-xs text-slate-500 border-t border-slate-200 pt-2 flex items-center gap-1.5">
                        <Info className="h-3.5 w-3.5 shrink-0" />
                        <span>{verifyResult.disclaimer}</span>
                      </div>
                    </div>
                  )}
                </form>
              </Card>
            </div>
          )}
        </div>
      </div>
    </PageShell>
  );
}
