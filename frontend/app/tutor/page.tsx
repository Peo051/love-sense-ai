'use client';

import { useEffect, useState } from 'react';
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
  History,
  Info,
  Layers,
  Lightbulb,
  Loader2,
  PlusCircle,
  RefreshCw,
  ShieldAlert,
  Sparkles,
  Terminal,
  User,
} from 'lucide-react';

import { ErrorAlert, InfoAlert, SuccessAlert, WarningAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import FieldLabel from '@/components/common/FieldLabel';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import {
  analyzeTutorCode,
  hasAuthToken,
  requestTutorNextHint,
  verifyTutorRetry,
} from '@/lib/api';
import type { OcrExtractionResult } from '@/lib/ocr';
import type {
  TimelineTurnItem,
  TimelineTurnType,
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

  // Authentication & Guest State
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [guestContextToken, setGuestContextToken] = useState<string | null>(null);

  // Multi-turn State & Attempt History
  const [currentAttemptIndex, setCurrentAttemptIndex] = useState(1);
  const [attemptsHistory, setAttemptsHistory] = useState<
    Array<{
      attemptIndex: number;
      initialCode: string;
      resolved: boolean;
      timestamp: string;
    }>
  >([]);
  const [turns, setTurns] = useState<TimelineTurnItem[]>([]);

  // Tutor & Verification State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isLoadingHint, setIsLoadingHint] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [tutorResult, setTutorResult] = useState<TutorResponse | null>(null);
  const [currentHintLevel, setCurrentHintLevel] = useState(1);
  const [highestHintLevel, setHighestHintLevel] = useState(1);
  const [solutionRevealed, setSolutionRevealed] = useState(false);

  const [revisedCode, setRevisedCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState<TutorVerifyResponse | null>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);

  useEffect(() => {
    setIsAuthenticated(hasAuthToken());
  }, []);

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
        save_input: isAuthenticated,
        save_result: isAuthenticated,
      });

      setTutorResult(response);
      setCurrentHintLevel(response.hint_level || 1);
      setHighestHintLevel(response.highest_hint_level_used || response.hint_level || 1);
      setSolutionRevealed(Boolean(response.solution_revealed));
      setRevisedCode(studentCode.trim());

      if (response.session_id) {
        setSessionId(response.session_id);
      }
      if (response.guest_context_token) {
        setGuestContextToken(response.guest_context_token);
      }

      const now = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const newTurns: TimelineTurnItem[] = [];

      // Turn 1: Student Question / Submission
      newTurns.push({
        id: `turn-q-${Date.now()}`,
        turnType: 'student_question',
        timestamp: now,
        content: studentQuestion.trim() || 'Nộp mã nguồn và yêu cầu gia sư hướng dẫn tư duy tự giải quyết.',
        codeSnippet: studentCode.trim(),
        attemptIndex: currentAttemptIndex,
      });

      // Turn 2: Tutor Initial Socratic Diagnosis
      newTurns.push({
        id: `turn-diag-${Date.now() + 1}`,
        turnType: 'tutor_diagnosis',
        timestamp: now,
        content: response.tutor_response,
        hintLevel: response.hint_level || 1,
        evidence: response.evidence,
        diagnosis: response.diagnosis,
        nextAction: response.next_action,
        attemptIndex: currentAttemptIndex,
      });

      setTurns((prev) => [...prev, ...newTurns]);
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
        session_id: sessionId || tutorResult.session_id,
        guest_context_token: guestContextToken || tutorResult.guest_context_token,
        current_hint_level: currentHintLevel,
        current_diagnosis: tutorResult.diagnosis,
        student_code: studentCode,
      });

      setCurrentHintLevel(nextHintRes.hint_level);
      setHighestHintLevel(nextHintRes.highest_hint_level_used);
      setSolutionRevealed(nextHintRes.solution_revealed);

      if (nextHintRes.guest_context_token) {
        setGuestContextToken(nextHintRes.guest_context_token);
      }

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

      const now = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
      const hintTurn: TimelineTurnItem = {
        id: `turn-hint-${Date.now()}`,
        turnType: 'next_hint',
        timestamp: now,
        content: nextHintRes.tutor_response,
        hintLevel: nextHintRes.hint_level,
        nextAction: nextHintRes.next_action,
        attemptIndex: currentAttemptIndex,
      };

      setTurns((prev) => [...prev, hintTurn]);
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
        session_id: sessionId || tutorResult.session_id,
        guest_context_token: guestContextToken || tutorResult.guest_context_token,
      });

      setVerifyResult(res);

      const now = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });

      // Turn 3: Student Retry Submission
      const retryTurn: TimelineTurnItem = {
        id: `turn-retry-${Date.now()}`,
        turnType: 'student_retry',
        timestamp: now,
        content: 'Sinh viên đã chỉnh sửa và gửi lại mã nguồn để xác minh.',
        codeSnippet: revisedCode.trim(),
        attemptIndex: currentAttemptIndex,
      };

      // Turn 4: Tutor Verification Evaluation
      const verifyTurn: TimelineTurnItem = {
        id: `turn-verif-${Date.now() + 1}`,
        turnType: 'tutor_verification',
        timestamp: now,
        content: res.feedback,
        verificationStatus: res.status,
        remainingIssues: res.remaining_issues,
        newIssues: res.new_issues,
        nextAction: res.next_action,
        disclaimer: res.disclaimer,
        diagnosis: res.diagnosis,
        attemptIndex: currentAttemptIndex,
      };

      setTurns((prev) => [...prev, retryTurn, verifyTurn]);
    } catch (err: any) {
      setVerifyError(err.message || 'Không thể xác minh bài sửa lúc này. Vui lòng thử lại.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleStartNewAttempt = () => {
    if (!tutorResult && turns.length === 0) return;

    // Save current attempt to history
    setAttemptsHistory((prev) => [
      ...prev,
      {
        attemptIndex: currentAttemptIndex,
        initialCode: studentCode,
        resolved: verifyResult?.resolved || false,
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }),
      },
    ]);

    const nextAttempt = currentAttemptIndex + 1;
    setCurrentAttemptIndex(nextAttempt);

    // Keep revised code in editor if student modified it, or keep original code
    if (revisedCode.trim()) {
      setStudentCode(revisedCode.trim());
    }

    // Reset transient attempt states
    setCurrentHintLevel(1);
    setHighestHintLevel(1);
    setSolutionRevealed(false);
    setVerifyResult(null);
    setVerifyError(null);
    setTutorResult(null);

    const now = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
    const newAttemptTurn: TimelineTurnItem = {
      id: `turn-new-attempt-${Date.now()}`,
      turnType: 'student_question',
      timestamp: now,
      content: `Bắt đầu lần thử mới #${nextAttempt} cho bài toán hiện tại. Mã nguồn đã được chuẩn bị lại.`,
      attemptIndex: nextAttempt,
    };
    setTurns((prev) => [...prev, newAttemptTurn]);
  };

  const confidenceInfo = tutorResult ? getCalibratedConfidence(tutorResult.diagnosis.confidence) : null;

  return (
    <PageShell className="space-y-8 pb-12">
      {/* Header & Session Identity Banner */}
      <section className="artistic-panel-bg relative overflow-hidden rounded-[2rem] border border-rose-200 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] sm:p-8">
        <div className="absolute inset-0 -z-0 bg-[radial-gradient(circle_at_top_left,rgba(244,63,94,0.12),transparent_28rem),radial-gradient(circle_at_top_right,rgba(15,118,110,0.1),transparent_24rem)]" />
        <div className="relative z-10 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
          <SectionHeader
            eyebrow="CodeSense AI Tutor • C# OOP"
            title="Không gian Gia Sư Lập Trình C# OOP"
            description="Không gian học tập đa lượt (Multi-turn Tutoring Session): Phân tích nguyên nhân lỗi, dẫn dắt tư duy Socratic từng bước, thử lại và xác minh bài sửa trong một luồng học liền mạch."
          />
          <div className="flex flex-wrap items-center gap-2 lg:justify-end">
            {isAuthenticated ? (
              <Badge tone="teal" className="flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Đã đăng nhập (Đồng bộ đám mây)
              </Badge>
            ) : (
              <Badge tone="amber" className="flex items-center gap-1">
                <ShieldAlert className="h-3.5 w-3.5" />
                Chế độ Khách (Không lưu trữ DB)
              </Badge>
            )}
            <Badge tone="rose">
              <Code2 className="h-3.5 w-3.5" aria-hidden="true" />
              Lần thử #{currentAttemptIndex}
            </Badge>
            <Badge tone="slate">
              <Cpu className="h-3.5 w-3.5" aria-hidden="true" />
              Socratic Progressive Hints
            </Badge>
          </div>
        </div>
      </section>

      {/* 3 Visibly Distinct Zones Layout */}
      <div className="space-y-6">
        {/* ZONE 1: Problem Statement & OOP Concept Focus */}
        <section
          aria-label="Khu vực Đề bài"
          className="rounded-[2rem] border-2 border-rose-100 bg-white p-6 shadow-sm transition hover:border-rose-200"
        >
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-rose-50 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-rose-100 text-rose-700 font-bold text-sm">
                1
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  Đề bài & Mục tiêu học tập (Problem Statement)
                </h2>
                <p className="text-xs text-slate-500">
                  Phân khu cố định: Giúp bạn luôn nắm vững yêu cầu bài toán trong suốt quá trình giải và sửa lỗi.
                </p>
              </div>
            </div>
            <div className="w-full sm:w-auto min-w-[260px]">
              <FieldLabel htmlFor="topic-select" label="Chủ đề OOP trọng tâm">
                <select
                  id="topic-select"
                  value={selectedTopic}
                  onChange={(e) => setSelectedTopic(e.target.value)}
                  className="w-full rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-800 focus:border-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-100"
                >
                  {oopTopics.map((t) => (
                    <option key={t.code} value={t.code}>
                      {t.label}
                    </option>
                  ))}
                </select>
              </FieldLabel>
            </div>
          </div>

          <FieldLabel
            htmlFor="problem-statement-input"
            label="Đề bài bài tập"
            hint="Mô tả chi tiết các yêu cầu kỹ thuật (lớp, trường dữ liệu, thuộc tính, ràng buộc)."
          >
            <textarea
              id="problem-statement-input"
              rows={3}
              value={problemStatement}
              onChange={(e) => setProblemStatement(e.target.value)}
              placeholder="Ví dụ: Tạo lớp BankAccount có trường số dư private và thuộc tính Balance kiểm tra value > 0..."
              className={textareaClassName}
            />
          </FieldLabel>
        </section>

        {/* 2-Column Split: ZONE 2 (Current Code Editor) & ZONE 3 (Tutor Conversation Timeline) */}
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(420px,0.9fr)] lg:items-start">
          {/* ZONE 2: Current Code Workspace */}
          <section
            aria-label="Khu vực Mã nguồn"
            className="space-y-6 rounded-[2rem] border-2 border-indigo-100 bg-white p-6 shadow-sm transition hover:border-indigo-200"
          >
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-indigo-50 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-indigo-100 text-indigo-700 font-bold text-sm">
                  2
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900">
                    Trình soạn thảo mã nguồn (Current Code Editor)
                  </h2>
                  <p className="text-xs text-slate-500">
                    Phân khu mã nguồn hiện tại: Nhập, chỉnh sửa và gửi phân tích lần thử mới.
                  </p>
                </div>
              </div>

              {turns.length > 0 && (
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={handleStartNewAttempt}
                  className="flex items-center gap-1.5"
                >
                  <PlusCircle className="h-3.5 w-3.5 text-indigo-600" />
                  Bắt đầu lần thử mới (New Attempt)
                </Button>
              )}
            </div>

            <div className="flex gap-2 border-b border-slate-200 pb-2">
              <button
                type="button"
                onClick={() => setActiveTab('editor')}
                className={`inline-flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                  activeTab === 'editor'
                    ? 'border border-indigo-200 bg-indigo-50 text-indigo-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <FileCode2 className="h-4 w-4" />
                Soạn thảo C#
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('ocr')}
                className={`inline-flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                  activeTab === 'ocr'
                    ? 'border border-indigo-200 bg-indigo-50 text-indigo-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Terminal className="h-4 w-4" />
                Quét từ ảnh bài tập (OCR)
              </button>
            </div>

            {activeTab === 'editor' ? (
              <form onSubmit={handleAnalyze} className="space-y-4">
                <FieldLabel
                  htmlFor="student-code-input"
                  label="Mã nguồn C# của bạn"
                  hint="Hỗ trợ phím Tab để thụt dòng. Mã nguồn được xử lý cách ly và bảo mật."
                >
                  <textarea
                    id="student-code-input"
                    rows={12}
                    value={studentCode}
                    onChange={(e) => setStudentCode(e.target.value)}
                    onKeyDown={handleCodeKeyDown}
                    placeholder={`// Dán mã nguồn C# của bạn tại đây...\npublic class BankAccount {\n    private decimal _balance;\n\n    public decimal Balance {\n        get { return _balance; }\n    }\n}`}
                    className={`${textareaClassName} font-mono text-sm leading-relaxed bg-slate-50/50`}
                  />
                </FieldLabel>

                <div className="grid gap-4 sm:grid-cols-2">
                  <FieldLabel
                    htmlFor="compiler-error-input"
                    label="Thông báo lỗi biên dịch (Compiler Error - tùy chọn)"
                    hint="Ví dụ: CS0122, CS0103..."
                  >
                    <input
                      id="compiler-error-input"
                      type="text"
                      value={compilerError}
                      onChange={(e) => setCompilerError(e.target.value)}
                      placeholder="Mã lỗi CSxxxx..."
                      className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-mono text-slate-800 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    />
                  </FieldLabel>

                  <FieldLabel
                    htmlFor="student-question-input"
                    label="Câu hỏi / Băn khoăn của bạn (tùy chọn)"
                    hint="Nêu thắc mắc để gia sư giải đáp cụ thể."
                  >
                    <input
                      id="student-question-input"
                      type="text"
                      value={studentQuestion}
                      onChange={(e) => setStudentQuestion(e.target.value)}
                      placeholder="Em chưa rõ cách kiểm tra value..."
                      className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-800 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
                    />
                  </FieldLabel>
                </div>

                {errorMessage && (
                  <ErrorAlert>
                    <p className="font-semibold text-red-950">{errorMessage}</p>
                  </ErrorAlert>
                )}

                <Button
                  type="submit"
                  size="lg"
                  className="w-full bg-indigo-600 hover:bg-indigo-700"
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

            {/* Previous Attempts Summary */}
            {attemptsHistory.length > 0 && (
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-3.5 space-y-2">
                <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                  <History className="h-4 w-4 text-slate-500" />
                  Lịch sử các lần thử trước:
                </div>
                <div className="space-y-1.5">
                  {attemptsHistory.map((att) => (
                    <div
                      key={att.attemptIndex}
                      className="flex items-center justify-between text-xs rounded-lg bg-white p-2 border border-slate-100"
                    >
                      <span className="font-medium text-slate-800">
                        Lần thử #{att.attemptIndex} ({att.timestamp})
                      </span>
                      <Badge tone={att.resolved ? 'teal' : 'amber'}>
                        {att.resolved ? 'Đã khắc phục' : 'Đang tiếp tục'}
                      </Badge>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* ZONE 3: Multi-turn Pedagogical Conversation Timeline */}
          <section
            aria-label="Khu vực Đối thoại Gia sư"
            className="space-y-6 rounded-[2rem] border-2 border-teal-100 bg-white p-6 shadow-sm transition hover:border-teal-200"
          >
            <div className="flex items-center gap-2.5 border-b border-teal-50 pb-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-teal-100 text-teal-700 font-bold text-sm">
                3
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  Đối thoại sư phạm đa lượt (Tutor Conversation)
                </h2>
                <p className="text-xs text-slate-500">
                  Dòng thời gian cấu trúc sư phạm: Câu hỏi &rarr; Chẩn đoán &rarr; Gợi ý &rarr; Thử lại &rarr; Xác minh.
                </p>
              </div>
            </div>

            {turns.length === 0 ? (
              <Card
                title="Tiến trình gợi ý Socratic 4 cấp độ"
                description="CodeSense AI không giải bài hộ mà giúp bạn tự khám phá ra giải pháp qua đối thoại sư phạm."
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
            ) : (
              <div className="space-y-5">
                {/* Pedagogical Timeline Turns */}
                <div className="space-y-4">
                  {turns.map((turn, index) => {
                    if (turn.turnType === 'student_question') {
                      return (
                        <div
                          key={turn.id || index}
                          className="rounded-2xl border border-indigo-100 bg-indigo-50/40 p-4 space-y-2 text-xs"
                        >
                          <div className="flex items-center justify-between text-indigo-900 font-bold">
                            <div className="flex items-center gap-1.5">
                              <User className="h-3.5 w-3.5 text-indigo-600" />
                              <span>Lần thử #{turn.attemptIndex || 1}: Học viên đặt vấn đề</span>
                            </div>
                            <span className="text-[11px] font-normal text-slate-400">{turn.timestamp}</span>
                          </div>
                          <p className="text-slate-800 text-sm">{turn.content}</p>
                        </div>
                      );
                    }

                    if (turn.turnType === 'tutor_diagnosis') {
                      return (
                        <Card
                          key={turn.id || index}
                          title="Chẩn đoán sư phạm"
                          description={`Lần thử #${turn.attemptIndex || 1} • Đánh giá kỹ thuật và bằng chứng đoạn mã`}
                        >
                          <div className="space-y-4 text-xs">
                            {/* Calibrated Confidence Badge */}
                            {confidenceInfo && (
                              <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
                                <div className="flex items-center gap-1.5">
                                  <confidenceInfo.icon
                                    className={`h-4 w-4 ${
                                      confidenceInfo.tone === 'teal'
                                        ? 'text-teal-600'
                                        : confidenceInfo.tone === 'amber'
                                        ? 'text-amber-600'
                                        : 'text-slate-600'
                                    }`}
                                  />
                                  <span className="font-semibold text-slate-800">{confidenceInfo.label}</span>
                                </div>
                                <Badge tone={confidenceInfo.tone}>
                                  {turn.diagnosis?.severity?.toUpperCase() || 'INFO'}
                                </Badge>
                              </div>
                            )}

                            {/* Category & Location */}
                            {turn.diagnosis && (
                              <div className="rounded-xl border border-slate-200 bg-white p-3 space-y-1">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                    Phân loại vấn đề
                                  </span>
                                  {turn.diagnosis.location && (
                                    <span className="text-[11px] font-mono text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
                                      Vị trí: {turn.diagnosis.location}
                                    </span>
                                  )}
                                </div>
                                <p className="text-sm font-bold text-slate-900">
                                  {categoryLabels[turn.diagnosis.category] || turn.diagnosis.issue_type}
                                </p>
                              </div>
                            )}

                            {/* Knowledge Components */}
                            {turn.diagnosis?.knowledge_components && turn.diagnosis.knowledge_components.length > 0 && (
                              <div className="space-y-1.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                  Khái niệm OOP liên quan
                                </span>
                                <div className="flex flex-wrap gap-1.5">
                                  {turn.diagnosis.knowledge_components.map((kc) => (
                                    <Badge key={kc} tone="teal">
                                      {kc}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Code Evidence */}
                            {turn.evidence && (
                              <div className="space-y-1.5">
                                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                  Bằng chứng đoạn mã liên quan
                                </span>
                                <div className="rounded-xl border border-slate-200 bg-slate-900 p-3 text-xs font-mono text-slate-100 overflow-x-auto">
                                  <pre className="whitespace-pre-wrap">{turn.evidence.code}</pre>
                                </div>
                                <p className="text-slate-600 italic">{turn.evidence.reason}</p>
                              </div>
                            )}

                            {/* Misconception */}
                            {turn.diagnosis?.possible_misconception && (
                              <div className="flex items-start gap-2.5 rounded-xl border border-amber-200 bg-amber-50/70 p-3">
                                <AlertCircle className="h-4 w-4 shrink-0 text-amber-600 mt-0.5" />
                                <div>
                                  <p className="font-bold text-amber-950">Gợi ý ngộ nhận tiềm ẩn:</p>
                                  <p className="mt-0.5 text-amber-900 leading-relaxed">
                                    {turn.diagnosis.possible_misconception.description}
                                  </p>
                                </div>
                              </div>
                            )}

                            {/* Socratic Response */}
                            <div className="rounded-xl border-2 border-rose-200 bg-rose-50/70 p-3.5 space-y-2">
                              <div className="flex items-center gap-1.5">
                                <Lightbulb className="h-4 w-4 text-rose-600" />
                                <h3 className="font-bold text-slate-900">
                                  Lời khuyên của Gia sư AI ({hintLevelNames[(turn.hintLevel || 1) - 1]})
                                </h3>
                              </div>
                              <p className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
                                {turn.content}
                              </p>
                              {turn.nextAction && (
                                <div className="flex items-center gap-1.5 rounded-lg bg-white/80 p-2 text-xs font-medium text-slate-700 border border-rose-100">
                                  <ArrowRight className="h-3.5 w-3.5 text-rose-600 shrink-0" />
                                  <span>Bước tiếp theo: {turn.nextAction}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </Card>
                      );
                    }

                    if (turn.turnType === 'next_hint') {
                      return (
                        <div
                          key={turn.id || index}
                          className="rounded-2xl border-2 border-teal-200 bg-teal-50/60 p-4 space-y-2 text-xs"
                        >
                          <div className="flex items-center justify-between text-teal-900 font-bold">
                            <div className="flex items-center gap-1.5">
                              <BookOpen className="h-4 w-4 text-teal-600" />
                              <span>Gợi ý tiếp theo ({hintLevelNames[(turn.hintLevel || 2) - 1]})</span>
                            </div>
                            <span className="text-[11px] font-normal text-slate-400">{turn.timestamp}</span>
                          </div>
                          <p className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
                            {turn.content}
                          </p>
                          {turn.nextAction && (
                            <div className="flex items-center gap-1.5 rounded-lg bg-white/80 p-2 text-xs font-medium text-slate-700 border border-teal-100">
                              <ArrowRight className="h-3.5 w-3.5 text-teal-600 shrink-0" />
                              <span>Bước tiếp theo: {turn.nextAction}</span>
                            </div>
                          )}
                        </div>
                      );
                    }

                    if (turn.turnType === 'student_retry') {
                      return (
                        <div
                          key={turn.id || index}
                          className="rounded-2xl border border-slate-300 bg-slate-50 p-4 space-y-2 text-xs"
                        >
                          <div className="flex items-center justify-between font-bold text-slate-800">
                            <div className="flex items-center gap-1.5">
                              <RefreshCw className="h-3.5 w-3.5 text-slate-600" />
                              <span>Lần sửa đổi của học viên (Attempt #{turn.attemptIndex || 1})</span>
                            </div>
                            <span className="text-[11px] font-normal text-slate-400">{turn.timestamp}</span>
                          </div>
                          <p className="text-slate-600">{turn.content}</p>
                          {turn.codeSnippet && (
                            <div className="rounded-xl border border-slate-200 bg-slate-900 p-2.5 font-mono text-slate-100 overflow-x-auto text-[11px]">
                              <pre className="whitespace-pre-wrap">{turn.codeSnippet}</pre>
                            </div>
                          )}
                        </div>
                      );
                    }

                    if (turn.turnType === 'tutor_verification') {
                      return (
                        <div
                          key={turn.id || index}
                          className="rounded-2xl border-2 border-emerald-200 bg-emerald-50/50 p-4 space-y-3 text-xs"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5 font-bold text-emerald-950">
                              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                              <span>Kết quả xác minh lần thử</span>
                            </div>
                            <Badge
                              tone={
                                turn.verificationStatus === 'likely_resolved'
                                  ? 'teal'
                                  : turn.verificationStatus === 'still_present'
                                  ? 'amber'
                                  : turn.verificationStatus === 'new_issue'
                                  ? 'rose'
                                  : 'slate'
                              }
                            >
                              {turn.verificationStatus}
                            </Badge>
                          </div>

                          <p className="text-sm font-semibold text-slate-900">{turn.content}</p>

                          {turn.remainingIssues && turn.remainingIssues.length > 0 && (
                            <div className="text-xs text-amber-900 bg-amber-50 p-2.5 rounded-xl border border-amber-200">
                              <p className="font-bold">Vấn đề cần sửa tiếp:</p>
                              <ul className="list-disc pl-4 mt-1 space-y-0.5">
                                {turn.remainingIssues.map((issue, idx) => (
                                  <li key={idx}>{issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {turn.newIssues && turn.newIssues.length > 0 && (
                            <div className="text-xs text-red-900 bg-red-50 p-2.5 rounded-xl border border-red-200">
                              <p className="font-bold">Vấn đề mới phát sinh:</p>
                              <ul className="list-disc pl-4 mt-1 space-y-0.5">
                                {turn.newIssues.map((issue, idx) => (
                                  <li key={idx}>{issue}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {turn.disclaimer && (
                            <div className="text-[11px] text-slate-500 border-t border-slate-200 pt-2 flex items-center gap-1.5">
                              <Info className="h-3.5 w-3.5 shrink-0" />
                              <span>{turn.disclaimer}</span>
                            </div>
                          )}
                        </div>
                      );
                    }

                    return null;
                  })}
                </div>

                {/* Progressive Hint Progression Controls */}
                {tutorResult && (
                  <div className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
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
                )}

                {/* Card Retry & Verify Area */}
                {tutorResult && (
                  <Card
                    title="Sửa lại & Xác minh (Retry & Verify)"
                    description="Áp dụng gợi ý để chỉnh sửa mã nguồn và gửi yêu cầu xác minh trực tiếp không cần tải lại trang."
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
                        className="w-full bg-teal-600 text-white hover:bg-teal-700"
                        disabled={!revisedCode.trim() || isVerifying}
                        isLoading={isVerifying}
                      >
                        <RefreshCw className="h-4 w-4" />
                        {isVerifying ? 'Đang xác minh bài sửa...' : 'Xác minh lần thử lại'}
                      </Button>
                    </form>
                  </Card>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </PageShell>
  );
}
