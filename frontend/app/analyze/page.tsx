'use client';

import { useState } from 'react';

import AnalysisForm from '@/components/analyze/AnalysisForm';
import AnalysisResultPanel from '@/components/analyze/AnalysisResultPanel';
import Badge from '@/components/common/Badge';
import Card from '@/components/common/Card';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { analyzeEmotion } from '@/lib/api';
import type { AnalyzeRequest, AnalyzeResponse } from '@/lib/types';

export default function AnalyzePage() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (payload: AnalyzeRequest) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const analysis = await analyzeEmotion(payload);
      setResult(analysis);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể phân tích đoạn chat lúc này.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageShell className="space-y-8">
      <SectionHeader
        eyebrow="Phân tích hội thoại"
        title="Nhập đoạn chat và nhận gợi ý phản hồi an toàn"
        description="Luồng này chỉ phân tích nội dung bạn nhập thủ công. Ứng dụng không đọc trộm tin nhắn và không lưu chat nếu bạn chưa đồng ý."
        action={<Badge tone="teal">Mock mode an toàn cho demo</Badge>}
      />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(380px,0.92fr)] lg:items-start">
        <Card
          title="Thông tin đầu vào"
          description="Điền hội thoại và bối cảnh cần thiết. Các tùy chọn lưu dữ liệu luôn tách riêng và mặc định tắt."
          className="lg:sticky lg:top-24"
        >
          <AnalysisForm isLoading={isLoading} onAnalyze={handleAnalyze} />
        </Card>

        <AnalysisResultPanel result={result} error={errorMessage} loading={isLoading} />
      </div>
    </PageShell>
  );
}
