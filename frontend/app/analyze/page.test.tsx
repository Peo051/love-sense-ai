import { render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import AnalyzePage from './page';

const mockReplace = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    replace: mockReplace,
    push: vi.fn(),
    prefetch: vi.fn(),
  }),
}));

describe('AnalyzePage (Redirect to Tutor)', () => {
  beforeEach(() => {
    mockReplace.mockReset();
  });

  it('redirects user to /tutor and displays fallback redirect link', () => {
    render(<AnalyzePage />);

    expect(mockReplace).toHaveBeenCalledWith('/tutor');
    expect(screen.getByRole('heading', { name: /đang chuyển hướng sang gia sư lập trình/i })).toBeInTheDocument();

    const link = screen.getByRole('link', { name: /đi tới codesense tutor/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/tutor');
  });
});

