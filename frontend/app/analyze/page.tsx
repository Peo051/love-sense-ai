'use client';

import { useState } from 'react';

import AnalysisForm from '@/components/analyze/AnalysisForm';
import AnalysisResultPanel from '@/components/analyze/AnalysisResultPanel';
import Card from '@/components/common/Card';
import { analyzeEmotion } from '@/lib/api';
import type { AnalyzeRequest, AnalyzeResponse } from '@/lib/types';

export default function AnalyzePage() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (payload: AnalyzeRequest) => {
    setIsLoading(true);
    setErrorMessage('');
    setResult(null); // Clear previous result

    try {
      console.log('[Analyze] Sending request:', payload);
      const analysis = await analyzeEmotion(payload);
      console.log('[Analyze] Received response:', analysis);
      setResult(analysis);
    } catch (error) {
      console.error('[Analyze] Error:', error);
      setResult(null);
      setErrorMessage(error instanceof Error ? error.message : 'Không thể phân tích đoạn chat lúc này.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
      <div className="max-w-3xl space-y-3">
        <p className="text-sm font-semibold uppercase text-rose-700">Love Emotion MVP</p>
        <h1 className="text-3xl font-bold text-slate-950 sm:text-4xl">Phân tích sắc thái cảm xúc trong đoạn chat</h1>
        <p className="text-base leading-7 text-slate-600">
          Nhập đoạn hội thoại và bối cảnh cá nhân hóa để nhận nhận định tham khảo, gợi ý phản hồi nhẹ
          nhàng và cảnh báo an toàn.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(380px,0.9fr)] lg:items-start">
        <Card
          title="Thông tin đầu vào"
          description="Dữ liệu chỉ được gửi đến backend local để tạo mock response. MVP chưa lưu nội dung chat mặc định."
        >
          <AnalysisForm isLoading={isLoading} onAnalyze={handleAnalyze} />
        </Card>

        <AnalysisResultPanel result={result} errorMessage={errorMessage} />
      </div>
    </div>
  );
}
