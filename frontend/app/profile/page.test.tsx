import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ProfilePage from './page';

const loadedProfile = {
  user_profile: {
    nickname: 'An',
    primary_language: 'C# / .NET',
    communication_style: 'Nhập môn C# OOP',
    relationship_status: 'Nắm vững 4 tính chất OOP',
  },
  partner_profile: {
    nickname: '',
    likes: '',
    dislikes: '',
    texting_style: '',
    when_happy: '',
    when_sad: '',
    when_angry: '',
    likes_checkins: true,
    dislikes_repeated_questions: true,
    height_cm: null,
    weight_kg: null,
    appearance: '',
    private_notes: '',
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
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    window.localStorage.clear();
  });

  it('loads student profile data and saves edited profile back to the API without partner UI', async () => {
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
    await waitFor(() => expect(nicknameInput).toHaveValue('An'));
    // Ensure no partner UI exists
    expect(screen.queryByLabelText(/người ấy/i)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/chiều cao/i)).not.toBeInTheDocument();

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
      })
    );
  });

  it('deletes the profile after confirmation and resets the visible form', async () => {
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

    const dialog = await screen.findByRole('alertdialog', { name: /xóa hồ sơ cá nhân hóa/i });
    await user.click(within(dialog).getByRole('button', { name: /xóa hồ sơ cá nhân hóa/i }));

    await waitFor(() => expect(screen.getByText('Đã xóa hồ sơ cá nhân hóa.')).toBeInTheDocument());
    expect(screen.getByLabelText(/^Biệt danh$/i)).toHaveValue('');
  });
});
