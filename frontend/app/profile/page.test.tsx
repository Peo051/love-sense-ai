import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ProfilePage from './page';

const loadedProfile = {
  user_profile: {
    nickname: 'An',
    primary_language: 'Tiếng Việt',
    communication_style: 'Nhẹ nhàng',
    relationship_status: 'Đang tìm hiểu',
  },
  partner_profile: {
    nickname: 'Bình',
    likes: 'Nhạc acoustic',
    dislikes: 'Bị hỏi dồn',
    texting_style: 'Trả lời chậm khi bận',
    when_happy: 'Nhắn nhiều hơn',
    when_sad: 'Ít nói',
    when_angry: 'Cần không gian riêng',
    likes_checkins: true,
    dislikes_repeated_questions: true,
    height_cm: 165,
    weight_kg: 55,
    appearance: '',
    private_notes: 'Ghi chú riêng',
  },
  updated_at: '2026-04-27T08:00:00.000Z',
};

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('ProfilePage', () => {
  beforeEach(() => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    vi.stubGlobal('confirm', vi.fn(() => true));
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('loads profile data and saves edited profile back to the API', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith('/api/profile') && init?.method === 'POST') {
        const payload = JSON.parse(String(init.body));
        return jsonResponse({ ...payload, updated_at: '2026-04-27T09:00:00.000Z' });
      }

      return jsonResponse(loadedProfile);
    });
    vi.stubGlobal('fetch', fetchMock);

    const user = userEvent.setup();
    render(<ProfilePage />);

    const nicknameInput = await screen.findByLabelText(/^Biệt danh$/i);
    expect(nicknameInput).toHaveValue('An');
    expect(screen.getByLabelText(/biệt danh người yêu/i)).toHaveValue('Bình');

    await user.clear(nicknameInput);
    await user.type(nicknameInput, 'An mới');
    await user.click(screen.getByRole('button', { name: /lưu hồ sơ/i }));

    await waitFor(() => expect(screen.getByText('Đã lưu hồ sơ cá nhân hóa.')).toBeInTheDocument());

    const postCall = fetchMock.mock.calls.find(
      ([input, init]) => String(input).endsWith('/api/profile') && init?.method === 'POST'
    );
    expect(postCall).toBeTruthy();
    expect(JSON.parse(String(postCall?.[1]?.body))).toEqual(
      expect.objectContaining({
        user_profile: expect.objectContaining({ nickname: 'An mới' }),
        partner_profile: expect.objectContaining({ nickname: 'Bình' }),
      })
    );
  });

  it('deletes the profile and resets the visible form', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);

      if (url.endsWith('/api/profile') && init?.method === 'DELETE') {
        return jsonResponse({ deleted: true });
      }

      return jsonResponse(loadedProfile);
    });
    vi.stubGlobal('fetch', fetchMock);

    const user = userEvent.setup();
    render(<ProfilePage />);

    expect(await screen.findByLabelText(/^Biệt danh$/i)).toHaveValue('An');
    await user.click(screen.getByRole('button', { name: /xóa hồ sơ cá nhân hóa/i }));

    await waitFor(() => expect(screen.getByText('Đã xóa hồ sơ cá nhân hóa.')).toBeInTheDocument());
    expect(screen.getByLabelText(/^Biệt danh$/i)).toHaveValue('');
  });
});
