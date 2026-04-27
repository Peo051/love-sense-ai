import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import HistoryPage from './page';

const historyResponse = {
  items: [
    {
      id: 'history-1',
      analyzed_at: '2026-04-27T08:00:00.000Z',
      overall_emotion: 'mệt mỏi / né tránh nhẹ',
      confidence: 0.72,
      emotion_distribution: { mệt_mỏi: 0.35, né_tránh: 0.25 },
      summary: 'Đoạn chat có thể cho thấy người kia đang mệt.',
      context_note: 'Nên phản hồi nhẹ nhàng.',
      suggested_reply: 'Em nghỉ một chút nha.',
      warning: 'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.',
      save_input: false,
      save_result: true,
      chat_text: null,
    },
  ],
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('HistoryPage', () => {
  beforeEach(() => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    vi.stubGlobal('confirm', vi.fn(() => true));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('renders saved analysis history without original chat when save_input is false', async () => {
    const fetchMock = vi.fn(async () => jsonResponse(historyResponse));
    vi.stubGlobal('fetch', fetchMock);

    render(<HistoryPage />);

    expect(await screen.findAllByText('mệt mỏi / né tránh nhẹ')).toHaveLength(2);
    expect(screen.getByText('72% tin cậy')).toBeInTheDocument();
    expect(screen.getByText('Đoạn chat có thể cho thấy người kia đang mệt.')).toBeInTheDocument();
    expect(screen.getByText('Không lưu vì bạn chưa đồng ý lưu nội dung chat.')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/history',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer test-token' }),
      })
    );
  });

  it('clears all history from the page and calls the backend delete endpoint', async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith('/api/history') && init?.method === 'DELETE') {
        return jsonResponse({ deleted: true });
      }

      return jsonResponse(historyResponse);
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<HistoryPage />);

    expect(await screen.findAllByText('mệt mỏi / né tránh nhẹ')).toHaveLength(2);
    await user.click(screen.getByRole('button', { name: /xóa toàn bộ lịch sử phân tích/i }));

    await waitFor(() => expect(screen.getByText('Đã xóa toàn bộ lịch sử phân tích.')).toBeInTheDocument());
    expect(screen.getByText('Chưa có lịch sử')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/history',
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});
