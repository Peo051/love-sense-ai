import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import { extractTextFromImage, type OcrExtractionResult } from '@/lib/ocr';

vi.mock('@/lib/ocr', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/ocr')>();

  return {
    ...actual,
    extractTextFromImage: vi.fn(),
  };
});

function createOcrResult(
  text: string,
  options: { warnings?: string[]; confidence?: number; score?: number } = {}
): OcrExtractionResult {
  const warnings = options.warnings ?? [];

  return {
    text,
    rawText: text,
    confidence: options.confidence ?? 86,
    language: 'vie+eng',
    quality: {
      score: options.score ?? (warnings.length ? 0.35 : 0.92),
      warnings,
    },
  };
}

describe('ImageOcrUploader', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('renders the image upload section', () => {
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    expect(screen.getByText(/nhập từ ảnh chụp đoạn chat/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tải ảnh chụp đoạn chat/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i })).toBeDisabled();
  });

  it('rejects files that are not images', async () => {
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    const fileInput = screen.getByLabelText(/tải ảnh chụp đoạn chat/i);
    const invalidFile = new File(['not an image'], 'notes.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    expect(screen.getByText(/vui lòng chọn ảnh định dạng png, jpg, jpeg hoặc webp/i)).toBeInTheDocument();
    expect(extractTextFromImage).not.toHaveBeenCalled();
  });

  it('shows a preview when a valid image is selected', async () => {
    const user = userEvent.setup();
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    await user.upload(
      screen.getByLabelText(/tải ảnh chụp đoạn chat/i),
      new File(['fake image'], 'chat-preview.webp', { type: 'image/webp' })
    );

    expect(screen.getByText('chat-preview.webp')).toBeInTheDocument();
    expect(screen.getByAltText(/ảnh chụp đoạn chat đã chọn/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i })).toBeEnabled();
  });

  it('rejects images larger than 5MB', async () => {
    const user = userEvent.setup();
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    const fileInput = screen.getByLabelText(/tải ảnh chụp đoạn chat/i);
    const oversizedImage = new File([new Uint8Array(5 * 1024 * 1024 + 1)], 'large.png', {
      type: 'image/png',
    });

    await user.upload(fileInput, oversizedImage);

    expect(screen.getByText(/ảnh tối đa 5mb/i)).toBeInTheDocument();
    expect(extractTextFromImage).not.toHaveBeenCalled();
  });

  it('extracts text and notifies the parent component', async () => {
    const user = userEvent.setup();
    const onTextExtracted = vi.fn();
    let resolveOcr: (value: OcrExtractionResult) => void = () => undefined;
    vi.mocked(extractTextFromImage).mockImplementationOnce((_file, onProgress) => {
      onProgress?.({ status: 'recognizing', progress: 0.65 });
      return new Promise<OcrExtractionResult>((resolve) => {
        resolveOcr = resolve;
      });
    });

    render(<ImageOcrUploader onTextExtracted={onTextExtracted} />);

    const fileInput = screen.getByLabelText(/tải ảnh chụp đoạn chat/i);
    await user.upload(fileInput, new File(['fake image'], 'chat.png', { type: 'image/png' }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(screen.getByText(/đang nhận diện chữ/i)).toBeInTheDocument();
    const result = createOcrResult('A: Em sao vậy?\nB: Em mệt thôi.');
    resolveOcr(result);
    await waitFor(() => {
      expect(onTextExtracted).toHaveBeenCalledWith('A: Em sao vậy?\nB: Em mệt thôi.', result);
    });
    expect(screen.getByText(/đã trích xuất nội dung/i)).toBeInTheDocument();
  });

  it('shows a warning when OCR quality is low or text is too short', async () => {
    const user = userEvent.setup();
    vi.mocked(extractTextFromImage).mockResolvedValueOnce(
      createOcrResult('ok', {
        confidence: 42,
        warnings: ['OCR nhận diện quá ít nội dung, vui lòng thử ảnh rõ hơn hoặc nhập thủ công.'],
      })
    );
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), new File(['fake image'], 'chat.png', {
      type: 'image/png',
    }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(await screen.findByText(/ocr có thể chưa chính xác/i)).toBeInTheDocument();
    expect(screen.getByText(/ocr nhận diện quá ít nội dung/i)).toBeInTheDocument();
  });

  it('shows a friendly error when OCR fails', async () => {
    const user = userEvent.setup();
    vi.mocked(extractTextFromImage).mockRejectedValueOnce(new Error('OCR failed'));
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    const fileInput = screen.getByLabelText(/tải ảnh chụp đoạn chat/i);
    await user.upload(fileInput, new File(['fake image'], 'chat.jpg', { type: 'image/jpeg' }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(await screen.findByText(/không thể nhận diện chữ từ ảnh này/i)).toBeInTheDocument();
  });
});
