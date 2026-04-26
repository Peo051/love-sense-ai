'use client';

import Card from '@/components/common/Card';
import Button from '@/components/common/Button';

export default function PartnerProfileForm() {
  return (
    <Card title="Thông tin người yêu">
      <form className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Tên người yêu</label>
          <input type="text" className="w-full p-2 border rounded-lg" />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Tuổi</label>
          <input type="number" className="w-full p-2 border rounded-lg" />
        </div>
        
        <Button>Lưu thông tin</Button>
      </form>
    </Card>
  );
}
