import { render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import ProgressPage from './page';

describe('ProgressPage', () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    window.localStorage.clear();
  });

  it('renders auth required message when user is not logged in', () => {
    render(<ProgressPage />);

    expect(screen.getByRole('heading', { name: /tiến độ học tập c# oop/i })).toBeInTheDocument();
    expect(screen.getByText(/đăng nhập để xem tiến độ học tập/i)).toBeInTheDocument();
  });

  it('renders OOP modules and progress metrics when user is authenticated', () => {
    window.localStorage.setItem('love_emotion_auth_token', 'test-token');
    render(<ProgressPage />);

    expect(screen.getByText(/lộ trình kiến thức c# oop/i)).toBeInTheDocument();
    expect(screen.getByText(/1. Lớp & Đối tượng/i)).toBeInTheDocument();
    expect(screen.getByText(/2. Tính đóng gói/i)).toBeInTheDocument();
    expect(screen.getByText(/3. Tính kế thừa/i)).toBeInTheDocument();
    expect(screen.getByText(/4. Tính đa hình/i)).toBeInTheDocument();
    expect(screen.getByText(/5. Xử lý ngoại lệ/i)).toBeInTheDocument();
  });
});
