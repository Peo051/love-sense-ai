'use client';

import HistoryList from '@/components/history/HistoryList';
import HistoryDetail from '@/components/history/HistoryDetail';

export default function HistoryPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Lịch sử phân tích</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <HistoryList />
        </div>
        
        <div className="lg:col-span-2">
          <HistoryDetail />
        </div>
      </div>
    </div>
  );
}
