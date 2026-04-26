'use client';

import { useEffect, useMemo, useState } from 'react';
import { Trash2 } from 'lucide-react';

import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { clearHistory, deleteHistoryItem, getHistory } from '@/lib/api';
import type { HistoryItem } from '@/lib/types';

function formatDate(value: string) {
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');

  const selectedItem = useMemo(
    () => items.find((item) => item.id === selectedId) ?? items[0] ?? null,
    [items, selectedId]
  );

  useEffect(() => {
    getHistory()
      .then((history) => {
        setItems(history.items);
        setSelectedId(history.items[0]?.id ?? null);
      })
      .catch((error) => setErrorMessage(error instanceof Error ? error.message : 'Không thể tải lịch sử.'));
  }, []);

  const handleDeleteItem = async (id: string) => {
    setErrorMessage('');
    setStatusMessage('');

    try {
      await deleteHistoryItem(id);
      const remainingItems = items.filter((item) => item.id !== id);
      setItems(remainingItems);
      setSelectedId(remainingItems[0]?.id ?? null);
      setStatusMessage('Đã xóa lịch sử phân tích.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa lịch sử.');
    }
  };

  const handleClearHistory = async () => {
    setErrorMessage('');
    setStatusMessage('');

    try {
      await clearHistory();
      setItems([]);
      setSelectedId(null);
      setStatusMessage('Đã xóa toàn bộ lịch sử phân tích.');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa toàn bộ lịch sử.');
    }
  };

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase text-rose-700">Lịch sử phân tích</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">Các lần phân tích đã được bạn đồng ý lưu</h1>
        </div>
        <Button type="button" variant="secondary" disabled={items.length === 0} onClick={handleClearHistory}>
          <Trash2 className="h-4 w-4" aria-hidden="true" />
          Xóa toàn bộ lịch sử
        </Button>
      </div>

      {statusMessage && <p className="mb-4 rounded-md bg-teal-50 px-4 py-3 text-sm text-teal-800">{statusMessage}</p>}
      {errorMessage && <p className="mb-4 rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">{errorMessage}</p>}

      {items.length === 0 ? (
        <Card
          title="Chưa có lịch sử"
          description="Ứng dụng không lưu mặc định. Lịch sử chỉ xuất hiện khi bạn bật tùy chọn lưu kết quả tại trang phân tích."
        >
          <p className="text-sm leading-6 text-slate-600">
            Nếu bạn chỉ muốn xem kết quả một lần, hãy tiếp tục không chọn các checkbox lưu dữ liệu.
          </p>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
          <Card title="Danh sách">
            <div className="space-y-3">
              {items.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  className={`w-full rounded-lg border px-4 py-3 text-left transition ${
                    selectedItem?.id === item.id
                      ? 'border-rose-300 bg-rose-50'
                      : 'border-slate-100 bg-white hover:border-rose-200'
                  }`}
                >
                  <p className="font-semibold text-slate-950">{item.overall_emotion}</p>
                  <p className="mt-1 text-sm text-slate-500">{formatDate(item.analyzed_at)}</p>
                  <p className="mt-2 text-sm text-slate-600">{Math.round(item.confidence * 100)}% tin cậy</p>
                </button>
              ))}
            </div>
          </Card>

          {selectedItem && (
            <Card title="Chi tiết lịch sử">
              <div className="space-y-5 text-sm leading-6 text-slate-700">
                <DetailRow label="Thời gian" value={formatDate(selectedItem.analyzed_at)} />
                <DetailRow label="Cảm xúc tổng quan" value={selectedItem.overall_emotion} />
                <DetailRow label="Độ tin cậy" value={`${Math.round(selectedItem.confidence * 100)}%`} />
                <DetailRow label="Tóm tắt" value={selectedItem.summary} />
                <DetailRow label="Gợi ý phản hồi" value={selectedItem.suggested_reply} />
                <DetailRow label="Cảnh báo an toàn" value={selectedItem.warning} />
                <div>
                  <p className="font-semibold text-slate-950">Nội dung chat gốc</p>
                  <p className="mt-2 rounded-lg bg-slate-50 px-4 py-3">
                    {selectedItem.chat_text ?? 'Không lưu vì bạn chưa đồng ý lưu nội dung chat.'}
                  </p>
                </div>
                <Button type="button" variant="secondary" onClick={() => handleDeleteItem(selectedItem.id)}>
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                  Xóa lịch sử này
                </Button>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="font-semibold text-slate-950">{label}</p>
      <p className="mt-1">{value}</p>
    </div>
  );
}
