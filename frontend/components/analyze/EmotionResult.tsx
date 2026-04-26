import Card from '@/components/common/Card';

export default function EmotionResult() {
  return (
    <Card title="Kết quả phân tích">
      <div className="space-y-4">
        <div>
          <p className="text-sm text-gray-600">Cảm xúc chính</p>
          <p className="text-2xl font-bold text-pink-600">Hạnh phúc</p>
        </div>
        
        <div>
          <p className="text-sm text-gray-600">Độ tin cậy</p>
          <p className="text-xl font-semibold">85%</p>
        </div>
      </div>
    </Card>
  );
}
