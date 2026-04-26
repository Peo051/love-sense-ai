'use client';

import Card from '@/components/common/Card';

export default function HistoryDetail() {
  return (
    <Card title="Chi tiết phân tích">
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600">Tin nhắn</p>
          <p className="mt-2 p-4 bg-gray-50 rounded-lg">
            Em nhớ anh quá!
          </p>
        </div>
        
        <div>
          <p className="text-sm text-gray-600">Cảm xúc phát hiện</p>
          <p className="text-xl font-bold text-pink-600 mt-2">Hạnh phúc</p>
        </div>
        
        <div>
          <p className="text-sm text-gray-600">Gợi ý đã dùng</p>
          <p className="mt-2 p-4 bg-gray-50 rounded-lg">
            Anh cũng nhớ em lắm!
          </p>
        </div>
      </div>
    </Card>
  );
}
