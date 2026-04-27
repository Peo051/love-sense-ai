'use client';

import { FormEvent, useState } from 'react';
import { Loader2, Send, ShieldCheck } from 'lucide-react';

import { ErrorAlert, InfoAlert } from '@/components/common/Alerts';
import Button from '@/components/common/Button';
import FieldLabel from '@/components/common/FieldLabel';
import type { AnalyzeRequest } from '@/lib/types';

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
    <form onSubmit={handleSubmit} className="space-y-5">
      <FieldLabel
        htmlFor="chat_text"
        label="Đoạn chat cần phân tích"
        hint="Chỉ nhập nội dung bạn có quyền sử dụng. Ứng dụng không tự đọc tin nhắn từ nền tảng khác."
      >
        <textarea
          id="chat_text"
          value={chatText}
          onChange={(event) => setChatText(event.target.value)}
          className="min-h-72 w-full resize-y rounded-2xl border border-rose-100 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
          placeholder="Dán hoặc nhập đoạn chat thủ công tại đây..."
        />
      </FieldLabel>

      <FieldLabel
        htmlFor="profile_context"
        label="Bối cảnh cá nhân hóa"
        hint="Không bắt buộc. Nên mô tả phong cách giao tiếp, thói quen phản hồi hoặc điều nên tránh."
      >
        <textarea
          id="profile_context"
          value={profileContext}
          onChange={(event) => setProfileContext(event.target.value)}
          className="min-h-36 w-full resize-y rounded-2xl border border-rose-100 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
          placeholder="Ví dụ: người ấy thường im lặng khi mệt, thích được lắng nghe trước khi nhận lời khuyên..."
        />
      </FieldLabel>

      <div className="grid gap-3">
        <label className="flex items-start gap-3 rounded-2xl border border-teal-200 bg-teal-50/80 px-4 py-3 text-sm leading-6 text-teal-950">
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
            className="mt-1 h-4 w-4 rounded border-teal-300 text-rose-600 focus:ring-rose-500"
          />
          <span>
            Tôi muốn lưu kết quả phân tích vào lịch sử. Nếu không chọn, kết quả chỉ hiển thị trong phiên hiện tại.
          </span>
        </label>

        <label className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50/80 px-4 py-3 text-sm leading-6 text-amber-950">
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
            Tôi đồng ý lưu nội dung đoạn chat này để xem lại trong lịch sử. Nếu không chọn, hệ thống không lưu chat gốc.
          </span>
        </label>
      </div>

      {validationError && <ErrorAlert>{validationError}</ErrorAlert>}

      <InfoAlert>
        <span className="inline-flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 shrink-0 text-teal-600" aria-hidden="true" />
          Không đọc trộm, không kết luận chắc chắn, không lưu chat nếu bạn chưa đồng ý.
        </span>
      </InfoAlert>

      <Button type="submit" isLoading={isLoading} className="w-full">
        {isLoading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Send className="h-4 w-4" aria-hidden="true" />}
        {isLoading ? 'Đang phân tích' : 'Phân tích'}
      </Button>
    </form>
  );
}
