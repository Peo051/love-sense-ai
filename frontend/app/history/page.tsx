'use client';

import { useEffect, useMemo, useState } from 'react';
import { Search, Trash2 } from 'lucide-react';
import Link from 'next/link';

import { ErrorAlert, SuccessAlert } from '@/components/common/Alerts';
import Badge from '@/components/common/Badge';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import ConfirmDialog from '@/components/common/ConfirmDialog';
import { EmptyState, LoadingState } from '@/components/common/StateBlocks';
import PageShell from '@/components/common/PageShell';
import SectionHeader from '@/components/common/SectionHeader';
import { clearHistory, deleteHistoryItem, getHistory } from '@/lib/api';
import type { HistoryItem } from '@/lib/types';
import { inputClassName } from '@/lib/ui';
import { cn } from '@/lib/utils';

type PendingDelete = { type: 'all' } | { type: 'item'; id: string } | null;

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
  const [isDeleting, setIsDeleting] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<PendingDelete>(null);
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

  const confirmDelete = async () => {
    if (!pendingDelete) {
      return;
    }

    setIsDeleting(true);
    setErrorMessage('');
    setStatusMessage('');

    try {
      if (pendingDelete.type === 'all') {
        await clearHistory();
        setItems([]);
        setSelectedId(null);
        setStatusMessage('Đã xóa toàn bộ lịch sử phân tích.');
      } else {
        await deleteHistoryItem(pendingDelete.id);
        const remainingItems = items.filter((item) => item.id !== pendingDelete.id);
        setItems(remainingItems);
        setSelectedId(remainingItems[0]?.id ?? null);
        setStatusMessage('Đã xóa lịch sử phân tích.');
      }
      setPendingDelete(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Không thể xóa lịch sử.');
    } finally {
      setIsDeleting(false);
    }
  };

  const pendingDeleteTitle =
    pendingDelete?.type === 'all' ? 'Xóa toàn bộ lịch sử?' : 'Xóa lịch sử phân tích này?';
  const pendingDeleteDescription =
    pendingDelete?.type === 'all'
      ? 'Thao tác này xóa mọi kết quả phân tích đã lưu của tài khoản hiện tại. Nội dung đã xóa không thể khôi phục.'
      : 'Thao tác này chỉ xóa mục lịch sử đang chọn của tài khoản hiện tại.';

  return (
    <PageShell className="space-y-8 pb-12">
      <SectionHeader
        eyebrow="Lịch sử phân tích"
        title="Những kết quả bạn đã đồng ý lưu"
        description="Danh sách này chỉ chứa dữ liệu của tài khoản hiện tại. Chat gốc chỉ xuất hiện khi bạn đã bật lưu nội dung chat."
        action={
          <Button
            type="button"
            variant="danger"
            disabled={items.length === 0}
            onClick={() => setPendingDelete({ type: 'all' })}
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
        <LoadingState
          title="Đang tải lịch sử"
          description="Đang tải các lần phân tích đã được lưu cho tài khoản hiện tại."
        />
      ) : items.length === 0 ? (
        <EmptyState
          title="Chưa có lịch sử"
          description="Ứng dụng không lưu mặc định. Lịch sử chỉ xuất hiện khi bạn bật tùy chọn lưu kết quả ở trang phân tích."
          action={
            <Link
              href="/analyze"
              className="inline-flex min-h-11 items-center justify-center rounded-xl border-2 border-slate-950 bg-blue-600 px-5 py-2.5 text-sm font-black text-white shadow-[5px_5px_0_#111827] transition hover:-translate-y-0.5 hover:bg-violet-600 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2"
            >
              Phân tích đoạn chat mới
            </Link>
          }
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[390px_minmax(0,1fr)]">
          <Card title="Danh sách" description="Tìm theo sắc thái, tóm tắt hoặc gợi ý phản hồi.">
            <div className="relative mb-4">
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Tìm trong lịch sử..."
                aria-label="Tìm trong lịch sử phân tích"
                className={cn(inputClassName, 'pl-10')}
              />
            </div>

            <div className="space-y-3">
              {filteredItems.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setSelectedId(item.id)}
                  aria-pressed={selectedItem?.id === item.id}
                  className={cn(
                    'w-full rounded-2xl border-2 px-3 py-3 text-left transition focus:outline-none focus:ring-4 focus:ring-blue-200 focus:ring-offset-2 min-[390px]:px-4',
                    selectedItem?.id === item.id
                      ? 'border-slate-950 bg-blue-50 shadow-[4px_4px_0_rgba(17,24,39,0.16)]'
                      : 'border-slate-950 bg-white hover:-translate-y-0.5 hover:bg-blue-50/60 hover:shadow-[4px_4px_0_rgba(17,24,39,0.12)]'
                  )}
                >
                  <div className="flex flex-col gap-2 min-[430px]:flex-row min-[430px]:items-start min-[430px]:justify-between">
                    <div className="min-w-0">
                      <p className="break-words font-semibold text-slate-950">{item.overall_emotion}</p>
                      <p className="mt-1 text-xs text-slate-500">{formatDate(item.analyzed_at)}</p>
                    </div>
                    <Badge tone={item.chat_text ? 'teal' : 'slate'} className="self-start">
                      {item.chat_text ? 'Có chat gốc' : 'Không lưu chat'}
                    </Badge>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-600">{summarize(item.summary)}</p>
                  <p className="mt-2 font-mono text-sm font-bold text-blue-700">{Math.round(item.confidence * 100)}% tin cậy</p>
                </button>
              ))}
            </div>
          </Card>

          {selectedItem ? (
            <Card title="Chi tiết lịch sử" className="lg:sticky lg:top-24">
              <div className="space-y-5 text-sm leading-6 text-slate-700">
                <DetailRow label="Thời gian" value={formatDate(selectedItem.analyzed_at)} />
                <DetailRow label="Cảm xúc tổng quan" value={selectedItem.overall_emotion} />
                <DetailRow label="Độ tin cậy" value={`${Math.round(selectedItem.confidence * 100)}%`} />
                <DetailRow label="Tóm tắt" value={selectedItem.summary} />
                <DetailRow label="Gợi ý phản hồi" value={selectedItem.suggested_reply} />
                <DetailRow label="Cảnh báo an toàn" value={selectedItem.warning} />
                {selectedItem.evidence && selectedItem.evidence.length > 0 ? (
                  <div>
                    <p className="font-semibold text-slate-950">Câu làm căn cứ</p>
                    <div className="mt-2 grid gap-2">
                      {selectedItem.evidence.map((item, index) => (
                        <div
                          key={`${item.quote}-${index}`}
                          className="rounded-2xl border-2 border-slate-950 bg-blue-50/70 px-4 py-3 shadow-[3px_3px_0_rgba(17,24,39,0.1)]"
                        >
                          <p className="font-mono text-xs font-bold uppercase tracking-[0.12em] text-blue-700">
                            {item.label}
                          </p>
                          <p className="mt-1 whitespace-pre-line text-slate-900">{item.quote}</p>
                          <p className="mt-1 text-slate-600">{item.reason}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : null}
                <div>
                  <p className="font-semibold text-slate-950">Nội dung chat gốc</p>
                  <p className="mt-2 rounded-2xl border-2 border-slate-950 bg-slate-50 px-4 py-3">
                    {selectedItem.chat_text ?? 'Không lưu vì bạn chưa đồng ý lưu nội dung chat.'}
                  </p>
                </div>
                <Button
                  type="button"
                  variant="danger"
                  className="w-full sm:w-auto"
                  onClick={() => setPendingDelete({ type: 'item', id: selectedItem.id })}
                  aria-label="Xóa lịch sử này"
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                  Xóa lịch sử này
                </Button>
              </div>
            </Card>
          ) : (
            <EmptyState
              title="Không tìm thấy kết quả"
              description="Thử xóa từ khóa tìm kiếm hoặc phân tích thêm một đoạn hội thoại mới."
              action={
                <Button type="button" variant="secondary" onClick={() => setQuery('')}>
                  Xóa tìm kiếm
                </Button>
              }
            />
          )}
        </div>
      )}

      <ConfirmDialog
        open={pendingDelete !== null}
        title={pendingDeleteTitle}
        description={pendingDeleteDescription}
        confirmLabel={pendingDelete?.type === 'all' ? 'Xóa toàn bộ lịch sử' : 'Xóa lịch sử phân tích'}
        isBusy={isDeleting}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
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
