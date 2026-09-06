import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import ProgressPage from './page';
import { getProgressDashboard } from '@/lib/api';
import type { StudentProgressDashboardResponse } from '@/lib/types';

vi.mock('@/lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/api')>();
  return {
    ...actual,
    getProgressDashboard: vi.fn(),
  };
});

const mockEmptyDashboard: StudentProgressDashboardResponse = {
  total_skills: 16,
  practiced_skills: 0,
  current_mastery_estimate: 0.5,
  is_empty: true,
  strong_topics: [],
  topics_needing_practice: [
    {
      skill_id: 'csharp.class_object',
      skill_name: 'Lớp và Đối tượng',
      mastery_score: 0.5,
      success_count: 0,
      failure_count: 0,
      hint_count: 0,
    },
    {
      skill_id: 'csharp.property',
      skill_name: 'Thuộc tính & Đóng gói',
      mastery_score: 0.5,
      success_count: 0,
      failure_count: 0,
      hint_count: 0,
    },
    {
      skill_id: 'csharp.constructor',
      skill_name: 'Hàm khởi tạo',
      mastery_score: 0.5,
      success_count: 0,
      failure_count: 0,
      hint_count: 0,
    },
  ],
  all_skills: [
    {
      skill_id: 'csharp.class_object',
      skill_name: 'Lớp và Đối tượng',
      mastery_score: 0.5,
      success_count: 0,
      failure_count: 0,
      hint_count: 0,
    },
  ],
  recent_attempts: [],
  average_hint_level: null,
  independent_solution_rate: null,
  total_attempts_count: 0,
  independent_success_count: 0,
};

const mockActiveDashboard: StudentProgressDashboardResponse = {
  total_skills: 16,
  practiced_skills: 2,
  current_mastery_estimate: 0.625,
  is_empty: false,
  strong_topics: [
    {
      skill_id: 'csharp.class_object',
      skill_name: 'Lớp và Đối tượng',
      mastery_score: 0.65,
      success_count: 1,
      failure_count: 0,
      hint_count: 0,
    },
  ],
  topics_needing_practice: [
    {
      skill_id: 'csharp.constructor',
      skill_name: 'Hàm khởi tạo',
      mastery_score: 0.45,
      success_count: 0,
      failure_count: 1,
      hint_count: 2,
    },
  ],
  all_skills: [
    {
      skill_id: 'csharp.class_object',
      skill_name: 'Lớp và Đối tượng',
      mastery_score: 0.65,
      success_count: 1,
      failure_count: 0,
      hint_count: 0,
    },
    {
      skill_id: 'csharp.property',
      skill_name: 'Thuộc tính & Đóng gói',
      mastery_score: 0.6,
      success_count: 1,
      failure_count: 0,
      hint_count: 1,
    },
    {
      skill_id: 'csharp.constructor',
      skill_name: 'Hàm khởi tạo',
      mastery_score: 0.45,
      success_count: 0,
      failure_count: 1,
      hint_count: 2,
    },
  ],
  recent_attempts: [
    {
      attempt_id: 'att-1',
      session_id: 'sess-1',
      problem_title: 'Tạo lớp BankAccount với số dư private',
      outcome: 'resolved',
      skills: ['csharp.class_object'],
      hints_used: 0,
      highest_hint_level: 0,
      created_at: '2026-09-06T10:00:00Z',
    },
    {
      attempt_id: 'att-2',
      session_id: 'sess-2',
      problem_title: 'Kiểm tra setter hợp lệ cho Balance',
      outcome: 'resolved',
      skills: ['csharp.property'],
      hints_used: 1,
      highest_hint_level: 1,
      created_at: '2026-09-06T10:15:00Z',
    },
  ],
  average_hint_level: 0.5,
  independent_solution_rate: 0.5,
  total_attempts_count: 2,
  independent_success_count: 1,
};

describe('ProgressPage (Student Learning Analytics Dashboard)', () => {
  beforeEach(() => {
    window.localStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it('renders auth required message when user is not logged in', () => {
    render(<ProgressPage />);

    expect(screen.getByRole('heading', { name: /bảng theo dõi tiến độ học tập c# oop/i })).toBeInTheDocument();
    expect(screen.getByText(/đăng nhập để xem tiến độ học tập/i)).toBeInTheDocument();
  });

  it('renders empty state when authenticated user has no attempts yet', async () => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    vi.mocked(getProgressDashboard).mockResolvedValueOnce(mockEmptyDashboard);

    render(<ProgressPage />);

    expect(await screen.findByRole('heading', { name: /chào mừng bạn đến với lộ trình c# oop/i })).toBeInTheDocument();
    expect(screen.getByText(/bạn chưa thực hiện lần thử bài tập nào/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.50 \/ 1\.0 \(neutral estimate\)/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /bắt đầu làm bài tập tại gia sư c# oop/i })).toBeInTheDocument();
  });

  it('renders full progress dashboard derived from actual backend data without hardcoded values', async () => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    vi.mocked(getProgressDashboard).mockResolvedValueOnce(mockActiveDashboard);

    render(<ProgressPage />);

    // 1. Overview metrics
    expect(await screen.findByText('2 / 16')).toBeInTheDocument();
    expect(screen.getByText('0.63 / 1.0')).toBeInTheDocument();
    expect(screen.getByText(/ước tính từ hệ thống \(system estimate\)/i)).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
    expect(screen.getByText(/1 bài thành công không cần gợi ý/i)).toBeInTheDocument();
    expect(screen.getByText('Cấp 0.5 / 4')).toBeInTheDocument();

    // 2. Strong topics
    expect(screen.getByRole('heading', { name: /chủ đề vững vàng/i })).toBeInTheDocument();
    expect(screen.getAllByText('Lớp và Đối tượng').length).toBeGreaterThan(0);
    expect(screen.getAllByText('0.65').length).toBeGreaterThan(0);

    // 3. Topics needing practice
    expect(screen.getByRole('heading', { name: /chủ đề cần luyện tập thêm/i })).toBeInTheDocument();
    expect(screen.getAllByText('Hàm khởi tạo').length).toBeGreaterThan(0);

    // 4. All skills taxonomy list
    expect(screen.getByRole('heading', { name: /lộ trình toàn bộ 16 kỹ năng c# oop/i })).toBeInTheDocument();
    expect(screen.getAllByText('Thuộc tính & Đóng gói').length).toBeGreaterThan(0);

    // 5. Recent attempts history
    expect(screen.getByRole('heading', { name: /lịch sử bài làm & lần thử gần nhất/i })).toBeInTheDocument();
    expect(screen.getByText('Tạo lớp BankAccount với số dư private')).toBeInTheDocument();
    expect(screen.getByText('Kiểm tra setter hợp lệ cho Balance')).toBeInTheDocument();
    expect(screen.getAllByText('Đã giải quyết').length).toBeGreaterThan(0);
  });

  it('handles API errors gracefully and allows retrying', async () => {
    const user = userEvent.setup();
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    vi.mocked(getProgressDashboard).mockRejectedValueOnce(new Error('Backend gặp lỗi kết nối.'));

    render(<ProgressPage />);

    expect(await screen.findByText('Backend gặp lỗi kết nối.')).toBeInTheDocument();
    const retryBtn = screen.getByRole('button', { name: /thử tải lại/i });
    expect(retryBtn).toBeInTheDocument();

    // Mock successful second call
    vi.mocked(getProgressDashboard).mockResolvedValueOnce(mockActiveDashboard);
    await user.click(retryBtn);

    expect(await screen.findByText('2 / 16')).toBeInTheDocument();
  });
});
