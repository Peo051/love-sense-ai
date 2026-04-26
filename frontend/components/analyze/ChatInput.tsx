'use client';

import { useState } from 'react';

export default function ChatInput() {
  const [message, setMessage] = useState('');

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium mb-2">
        Nhập tin nhắn cần phân tích
      </label>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        className="w-full p-4 border rounded-lg resize-none"
        rows={6}
        placeholder="Nhập tin nhắn từ người yêu của bạn..."
      />
    </div>
  );
}
