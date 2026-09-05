import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';

import TutorPage from './page';

describe('TutorPage', () => {
  it('renders tutor page heading and migration warning', () => {
    render(<TutorPage />);

    expect(screen.getByRole('heading', { name: /gia sư lập trình c# oop/i })).toBeInTheDocument();
    expect(screen.getByText(/tutor backend migration in progress/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/chủ đề oop/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/yêu cầu bài tập hoặc lỗi đang gặp/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mã nguồn c#/i)).toBeInTheDocument();
  });

  it('allows user to type code and switch to OCR tab', async () => {
    const user = userEvent.setup();
    render(<TutorPage />);

    const codeInput = screen.getByLabelText(/mã nguồn c#/i);
    fireEvent.change(codeInput, { target: { value: 'public class Car {}' } });
    expect(codeInput).toHaveValue('public class Car {}');

    const ocrTabButton = screen.getByRole('button', { name: /quét từ ảnh chụp bài tập/i });
    await user.click(ocrTabButton);

    expect(screen.getByRole('heading', { name: /quét mã nguồn từ ảnh bài tập/i })).toBeInTheDocument();
  });
});
