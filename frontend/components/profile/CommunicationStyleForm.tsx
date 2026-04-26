'use client';

import Card from '@/components/common/Card';
import Button from '@/components/common/Button';

export default function CommunicationStyleForm() {
  return (
    <Card title="Phong cách giao tiếp">
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Phong cách của bạn
          </label>
          <select className="w-full p-2 border rounded-lg">
            <option>Trực tiếp</option>
            <option>Gián tiếp</option>
            <option>Cảm xúc</option>
          </select>
        </div>
        
        <Button>Lưu phong cách</Button>
      </form>
    </Card>
  );
}
