'use client';

import Card from '@/components/common/Card';

export default function HistoryList() {
  const histories = [
    { id: 1, date: '2026-04-26', emotion: 'Hạnh phúc' },
    { id: 2, date: '2026-04-25', emotion: 'Yêu thương' },
    { id: 3, date: '2026-04-24', emotion: 'Quan tâm' },
  ];

  return (
    <Card title="Danh sách">
      <div className="space-y-2">
        {histories.map((history) => (
          <div
            key={history.id}
            className="p-3 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer"
          >
            <p className="font-semibold">{history.emotion}</p>
            <p className="text-sm text-gray-600">{history.date}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
