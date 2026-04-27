'use client';

import { FormEvent, useState } from 'react';
import { History, Loader2, LockKeyhole, Save, Send, ShieldCheck } from 'lucide-react';

import { ErrorAlert, InfoAlert } from '@/components/common/Alerts';
import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import FieldLabel from '@/components/common/FieldLabel';
import type { AnalyzeRequest } from '@/lib/types';
import { textareaClassName } from '@/lib/ui';

interface AnalysisFormProps {
  isLoading: boolean;
  onAnalyze: (payload: AnalyzeRequest) => Promise<void>;
}

const SAMPLE_CHAT = `A: Em sao vậy?
B: Không sao.
A: Anh thấy em hơi lạ.
B: Em mệt thôi.`;

export default function AnalysisForm({ isLoading, onAnalyze }: AnalysisFormProps) {
  const [chatText, setChatText] = useState(SAMPLE_CHAT);
  const [profileContext, setProfileContext] = useState(
    'Người ấy thường im lặng khi mệt, không thích bị hỏi dồn và cần được lắng nghe trước.'
  );
  const [saveResult, setSaveResult] = useState(false);
  const [saveInput, setSaveInput] = useState(false);
  const [validationError, setValidationError] = useState('');

  const handleOcrTextExtracted = (text: string) => {
    const nextText = text.trim();
    if (!nextText) {
      return;
    }

    if (chatText.trim()) {
      const shouldReplace = window.confirm(
        'Bạn muốn thay thế nội dung hiện tại bằng văn bản OCR không? Chọn Hủy để thêm vào cuối nội dung hiện có.'
      );

      if (!shouldReplace) {
        setChatText((currentText) => `${currentText.trimEnd()}\n\n${nextText}`.trim());
        return;
      }
    }

    setChatText(nextText);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!chatText.trim()) {
      setValidationError('Vui lòng nhập đoạn chat cần phân tích.');
      return;
    }

    setValidationError('');
    await onAnalyze({
      chat_text: chatText,
      profile_context: profileContext,
      save_input: saveInput,
      save_result: saveResult || saveInput,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <ImageOcrUploader onTextExtracted={handleOcrTextExtracted} />

      <Card
        title="Đoạn chat"
        description="Dán một đoạn hội thoại ngắn để hệ thống phân tích sắc thái. Không cần nhập thông tin cá nhân."
      >
        <FieldLabel
          htmlFor="chat_text"
          label="Đoạn chat cần phân tích"
          hint="Ứng dụng chỉ xử lý nội dung bạn nhập thủ công, không tự đọc tin nhắn từ nền tảng khác."
        >
          <textarea
            id="chat_text"
            value={chatText}
            onChange={(event) => setChatText(event.target.value)}
            className={`${textareaClassName} min-h-44 sm:min-h-72`}
            placeholder="Dán đoạn hội thoại ngắn tại đây. Không cần thông tin cá nhân."
          />
        </FieldLabel>
      </Card>

      <Card
        title="Bối cảnh cá nhân hóa"
        description="Phần này giúp gợi ý phản hồi bớt máy móc. Có thể bỏ trống nếu bạn chưa muốn thêm bối cảnh."
      >
        <FieldLabel
          htmlFor="profile_context"
          label="Bối cảnh cá nhân hóa"
          hint="Mô tả phong cách giao tiếp, thói quen phản hồi hoặc điều nên tránh."
        >
          <textarea
            id="profile_context"
            value={profileContext}
            onChange={(event) => setProfileContext(event.target.value)}
            className={`${textareaClassName} min-h-28 sm:min-h-36`}
            placeholder="Ví dụ: Người ấy thường im lặng khi mệt, không thích bị hỏi dồn..."
          />
        </FieldLabel>
      </Card>

      <Card title="Tùy chọn lưu dữ liệu" description="Bạn có thể phân tích mà không lưu gì. Các tùy chọn này mặc định tắt.">
        <div className="grid gap-3">
          <label className="flex items-start gap-3 rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 text-sm leading-6 text-slate-700 transition hover:border-rose-200 hover:bg-rose-50/50">
            <input
              type="checkbox"
              checked={saveResult}
              onChange={(event) => {
                const checked = event.target.checked;
                setSaveResult(checked);
                if (!checked) {
                  setSaveInput(false);
                }
              }}
              className="mt-1 h-4 w-4 rounded border-slate-300 text-rose-600 focus:ring-rose-500"
            />
            <span>
              <span className="flex items-start gap-2 font-semibold text-slate-950 sm:items-center">
                <History className="h-4 w-4 text-rose-600" aria-hidden="true" />
                Lưu kết quả phân tích vào lịch sử
              </span>
              <span className="mt-1 block">Chỉ lưu phần kết quả tổng hợp để bạn xem lại sau.</span>
            </span>
          </label>

          <label className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50/70 px-4 py-3 text-sm leading-6 text-amber-950 transition hover:border-amber-300 hover:bg-amber-50">
            <input
              type="checkbox"
              checked={saveInput}
              onChange={(event) => {
                const checked = event.target.checked;
                setSaveInput(checked);
                if (checked) {
                  setSaveResult(true);
                }
              }}
              className="mt-1 h-4 w-4 rounded border-amber-300 text-rose-600 focus:ring-rose-500"
            />
            <span>
              <span className="flex items-start gap-2 font-semibold text-amber-950 sm:items-center">
                <Save className="h-4 w-4 text-amber-700" aria-hidden="true" />
                Lưu nội dung chat gốc
              </span>
              <span className="mt-1 block">
                Chỉ bật khi bạn thật sự muốn xem lại nội dung chat trong lịch sử. Nếu không chọn, hệ thống không lưu chat
                gốc.
              </span>
            </span>
          </label>
        </div>
      </Card>

      {validationError && <ErrorAlert>{validationError}</ErrorAlert>}

      <InfoAlert>
        <span className="inline-flex items-start gap-2">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-teal-600" aria-hidden="true" />
          <span>Ứng dụng không lưu nội dung chat nếu bạn chưa đồng ý.</span>
        </span>
      </InfoAlert>

      <div className="rounded-2xl border border-rose-100 bg-white/90 p-3 shadow-sm">
        <Button type="submit" isLoading={isLoading} size="lg" className="w-full">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Send className="h-4 w-4" aria-hidden="true" />
          )}
          {isLoading ? 'Đang phân tích sắc thái' : 'Phân tích sắc thái'}
        </Button>
        <p className="mt-3 flex items-start gap-2 px-1 text-xs leading-5 text-slate-500">
          <LockKeyhole className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
          Không lưu chat mặc định. Bạn có thể bỏ qua toàn bộ tùy chọn lưu dữ liệu.
        </p>
      </div>
    </form>
  );
}
