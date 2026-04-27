import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import PrivacyPage from './page';

const consentResponse = {
  history_enabled: true,
  save_input: false,
  save_result: true,
  consent_type: 'privacy_settings',
  is_accepted: true,
  accepted_at: '2026-04-27T08:00:00.000Z',
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('PrivacyPage', () => {
  beforeEach(() => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('calls the correct delete endpoints for history, profile, and all user data after confirmation', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (init?.method === 'DELETE') {
        return jsonResponse({ deleted: true });
      }

      if (url.endsWith('/api/consent')) {
        return jsonResponse(consentResponse);
      }

      return jsonResponse({});
    });
    vi.stubGlobal('fetch', fetchMock);

    const user = userEvent.setup();
    render(<PrivacyPage />);

    expect(await screen.findByText('Cài đặt lưu dữ liệu')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /xóa lịch sử phân tích/i }));
    let dialog = await screen.findByRole('alertdialog', { name: /xóa lịch sử phân tích/i });
    await user.click(within(dialog).getByRole('button', { name: /xóa lịch sử phân tích/i }));
    await waitFor(() => expect(screen.getByText('Đã xóa lịch sử phân tích.')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /xóa hồ sơ cá nhân hóa/i }));
    dialog = await screen.findByRole('alertdialog', { name: /xóa hồ sơ cá nhân hóa/i });
    await user.click(within(dialog).getByRole('button', { name: /xóa hồ sơ cá nhân hóa/i }));
    await waitFor(() => expect(screen.getByText('Đã xóa hồ sơ cá nhân hóa.')).toBeInTheDocument());

    await user.click(screen.getByRole('button', { name: /xóa toàn bộ dữ liệu cá nhân/i }));
    dialog = await screen.findByRole('alertdialog', { name: /xóa toàn bộ dữ liệu cá nhân/i });
    await user.click(within(dialog).getByRole('button', { name: /xóa toàn bộ dữ liệu cá nhân/i }));
    await waitFor(() =>
      expect(screen.getByText('Đã xóa toàn bộ dữ liệu cá nhân của tài khoản hiện tại.')).toBeInTheDocument()
    );

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/history',
      expect.objectContaining({ method: 'DELETE' })
    );
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/profile',
      expect.objectContaining({ method: 'DELETE' })
    );
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/user-data',
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});
