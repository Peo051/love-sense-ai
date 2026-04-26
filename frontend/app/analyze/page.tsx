'use client';

import ChatInput from '@/components/analyze/ChatInput';
import AnalyzeButton from '@/components/analyze/AnalyzeButton';
import EmotionResult from '@/components/analyze/EmotionResult';
import EmotionChart from '@/components/analyze/EmotionChart';
import SuggestedReply from '@/components/analyze/SuggestedReply';

export default function AnalyzePage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Phân tích cảm xúc</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <ChatInput />
          <AnalyzeButton />
        </div>
        
        <div>
          <EmotionResult />
          <EmotionChart />
          <SuggestedReply />
        </div>
      </div>
    </div>
  );
}
