import Link from 'next/link';
import Button from '@/components/common/Button';

export default function HomePage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <div className="text-center">
        <h1 className="text-5xl font-bold mb-6">
          Love Emotion
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Phân tích cảm xúc trong các cuộc trò chuyện tình yêu của bạn
        </p>
        <Link href="/analyze">
          <Button>Bắt đầu phân tích</Button>
        </Link>
      </div>
    </div>
  );
}
