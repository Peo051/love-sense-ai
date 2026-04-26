'use client';

import Card from '@/components/common/Card';
import Button from '@/components/common/Button';

export default function PreferenceForm() {
  return (
    <Card title="Sở thích">
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Ngôn ngữ yêu thích
          </label>
          <select className="w-full p-2 border rounded-lg">
            <option>Tiếng Việt</option>
            <option>English</option>
          </select>
        </div>
        
        <Button>Lưu sở thích</Button>
      </form>
    </Card>
  );
}
