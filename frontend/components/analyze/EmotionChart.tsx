'use client';

import Card from '@/components/common/Card';

export default function EmotionChart() {
  const emotions = [
    { name: 'Hạnh phúc', value: 85 },
    { name: 'Yêu thương', value: 70 },
    { name: 'Quan tâm', value: 60 },
  ];

  return (
    <Card title="Biểu đồ cảm xúc" className="mt-4">
      <div className="space-y-3">
        {emotions.map((emotion) => (
          <div key={emotion.name}>
            <div className="flex justify-between mb-1">
              <span className="text-sm">{emotion.name}</span>
              <span className="text-sm font-semibold">{emotion.value}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-pink-600 h-2 rounded-full"
                style={{ width: `${emotion.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
