'use client';

import { useEffect, useMemo, useState } from 'react';
import { Search, Trash2 } from 'lucide-react';

import { ErrorAlert, SuccessAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { EmptyState, LoadingState } from '@/components/common/StateBlocks';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { clearHistory, deleteHistoryItem, getHistory } from '@/lib/api';
import type { HistoryItem } from '@/lib/types';

function formatDate(value: string) {
  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}

function summarize(text: string, length = 130) {
  return text.length > length ? `${text.slice(0, length)}...` : text;
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [query, setQuery] = useState('');

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    if (!normalizedQuery) {
      return items;
    }

    return items.filter((item) =>
      [item.overall_emotion, item.summary, item.suggested_reply].some((value) =>
        value.toLowerCase().includes(normalizedQuery)
      )
    );
  }, [items, query]);

  const selectedItem = useMemo(
    () => filteredItems.find((item) => item.id === selectedId) ?? filteredItems[0] ?? null,
    [filteredItems, selectedId]
  );

  useEffect(() => {
    getHistory()
      .then((history) => {
        setItems(history.items);
        setSelectedId(history.items[0]?.id ?? null);
      })
      .catch((error) => setErrorMessage(error instanceof Error ? error.message : 'Không thể tải lịch sử.'))
      .finally(() => setIsLoading(false));
  }, []);

  const handleDeleteItem = async (id: string) => {
    if (!window.confirm('Bạn có chắc muốn xóa lịch sử phân tích này không?')) {
      return;
    }

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
    if (!window.confirm('Bạn có chắc muốn xóa toàn bộ lịch sử phân tích không?')) {
      return;
    }

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
    <PageShell className="space-y-8">
      <SectionHeader
        eyebrow="Lịch sử phân tích"
        title="Những kết quả bạn đã đồng ý lưu"
        description="Danh sách này chỉ chứa dữ liệu của tài khoản hiện tại. Chat gốc chỉ xuất hiện khi bạn đã bật lưu nội dung chat."
        action={
          <Button
            type="button"
            variant="danger"
            disabled={items.length === 0}
            onClick={handleClearHistory}
            aria-label="Xóa toàn bộ lịch sử phân tích"
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
            Xóa toàn bộ
          </Button>
        }
      />

      {statusMessage && <SuccessAlert>{statusMessage}</SuccessAlert>}
      {errorMessage && <ErrorAlert>{errorMessage}</ErrorAlert>}

      {isLoading ? (
        <LoadingState title="Đang tải lịch sử" description="Đang tải các lần phân tích đã được lưu cho tài khoản hiện tại." />
      ) : items.length === 0 ? (
        <EmptyState
          title="Chưa có lịch sử"
          description="Ứng dụng không lưu mặc định. Lịch sử chỉ xuất hiện khi bạn bật tùy chọn lưu kết quả ở trang phân tích."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[390px_minmax(0,1fr)]">
          <Card title="Danh sách" description="Tìm theo sắc thái, tóm tắt hoặc gợi ý phản hồi.">
            <div className="mb-4 flex items-center gap-2 rounded-2xl border border-rose-100 bg-white px-3 py-2 focus-within:border-rose-400 focus-within:ring-4 focus-within:ring-rose-100">
              <Search className="h-4 w-4 text-slate-400" aria-hidden="true" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Tìm trong lịch sử..."
                aria-label="Tìm trong lịch sử phân tích"
                className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
              />
            </div>

            <div className="space-y-3">
              {filteredItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  aria-pressed={selectedItem?.id === item.id}
                  className={`w-full rounded-2xl border px-4 py-3 text-left transition focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 ${
                    selectedItem?.id === item.id
                      ? 'border-rose-300 bg-rose-50'
                      : 'border-slate-100 bg-white hover:border-rose-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold text-slate-950">{item.overall_emotion}</p>
                      <p className="mt-1 text-xs text-slate-500">{formatDate(item.analyzed_at)}</p>
                    </div>
                    <Badge tone={item.chat_text ? 'teal' : 'slate'}>{item.chat_text ? 'Có chat gốc' : 'Không lưu chat'}</Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{summarize(item.summary)}</p>
                  <p className="mt-2 text-sm font-medium text-rose-700">{Math.round(item.confidence * 100)}% tin cậy</p>
                </button>
              ))}
            </div>
          </Card>

          {selectedItem ? (
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
                  <p className="mt-2 rounded-2xl bg-slate-50 px-4 py-3">
                    {selectedItem.chat_text ?? 'Không lưu vì bạn chưa đồng ý lưu nội dung chat.'}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="danger"
                  onClick={() => handleDeleteItem(selectedItem.id)}
                  aria-label="Xóa lịch sử này"
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                  Xóa lịch sử này
                </Button>
              </div>
            </Card>
          ) : (
            <EmptyState title="Không tìm thấy kết quả" description="Thử xóa từ khóa tìm kiếm hoặc phân tích thêm một đoạn hội thoại mới." />
          )}
        </div>
      )}
    </PageShell>
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
