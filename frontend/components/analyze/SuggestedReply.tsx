import Card from '@/components/common/Card';

export default function SuggestedReply() {
  const suggestions = [
    'Em cũng rất nhớ anh!',
    'Anh làm em vui quá!',
    'Em yêu anh nhiều lắm!'
  ];

  return (
    <Card title="Gợi ý trả lời" className="mt-4">
      <div className="space-y-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="w-full text-left p-3 bg-gray-50 hover:bg-gray-100 rounded-lg"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </Card>
  );
}
