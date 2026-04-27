'use client';

import { FormEvent, useState } from 'react';
import { Loader2, Send, ShieldCheck } from 'lucide-react';

import Button from '@/components/common/Button';
import type { AnalyzeRequest } from '@/lib/types';

interface AnalysisFormProps {
  isLoading: boolean;
  onAnalyze: (payload: AnalyzeRequest) => Promise<void>;
}

const SAMPLE_CHAT = `Em sao vậy?
Không sao.
Anh thấy em hơi lạ.
Em mệt thôi.`;

export default function AnalysisForm({ isLoading, onAnalyze }: AnalysisFormProps) {
  const [chatText, setChatText] = useState(SAMPLE_CHAT);
  const [profileContext, setProfileContext] = useState(
    'Người yêu thường im lặng khi mệt, không thích bị hỏi dồn.'
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
      <div className="space-y-2">
        <label htmlFor="chat_text" className="text-sm font-semibold text-slate-800">
          Đoạn chat cần phân tích
        </label>
        <textarea
          id="chat_text"
          value={chatText}
          onChange={(event) => setChatText(event.target.value)}
          className="min-h-64 w-full resize-y rounded-lg border border-rose-100 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
          placeholder="Dán hoặc nhập đoạn chat thủ công tại đây..."
        />
      </div>

      <div className="space-y-2">
        <label htmlFor="profile_context" className="text-sm font-semibold text-slate-800">
          Bối cảnh cá nhân hóa
        </label>
        <textarea
          id="profile_context"
          value={profileContext}
          onChange={(event) => setProfileContext(event.target.value)}
          className="min-h-36 w-full resize-y rounded-lg border border-rose-100 bg-white px-4 py-3 text-sm leading-6 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-rose-400 focus:ring-4 focus:ring-rose-100"
          placeholder="Ví dụ: người ấy thường im lặng khi mệt, thích được lắng nghe trước khi nhận lời khuyên..."
        />
      </div>

      <label className="flex items-start gap-3 rounded-lg border border-teal-200 bg-teal-50 px-4 py-3 text-sm leading-6 text-teal-950">
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

      <label className="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">
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
          Tôi đồng ý lưu nội dung đoạn chat này để xem lại trong lịch sử. Nếu không chọn, ứng dụng chỉ lưu kết quả tổng
          hợp khi bạn đã bật lưu kết quả.
        </span>
      </label>

      {validationError && (
        <p role="alert" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
          {validationError}
        </p>
      )}

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="inline-flex items-center gap-2 text-sm text-slate-600">
          <ShieldCheck className="h-4 w-4 text-teal-600" aria-hidden="true" />
          Không đọc trộm, không kết luận chắc chắn, ưu tiên quyền riêng tư.
        </div>
        <Button type="submit" isLoading={isLoading} className="w-full sm:w-auto">
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          ) : (
            <Send className="h-4 w-4" aria-hidden="true" />
          )}
          {isLoading ? 'Đang phân tích' : 'Phân tích'}
        </Button>
      </div>
    </form>
  );
}
