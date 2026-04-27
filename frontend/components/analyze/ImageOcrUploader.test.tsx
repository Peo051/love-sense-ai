import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import ImageOcrUploader from '@/components/analyze/ImageOcrUploader';
import { extractChatTextWithVision } from '@/lib/api';
import { extractTextFromImage, type OcrExtractionResult } from '@/lib/ocr';

vi.mock('@/lib/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/api')>();

  return {
    ...actual,
    extractChatTextWithVision: vi.fn(),
  };
});

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

  it('renders the image upload section and OCR capture guidance', () => {
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    expect(screen.getByText(/nhập từ ảnh chụp đoạn chat/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tải ảnh chụp đoạn chat/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i })).toBeDisabled();
    expect(screen.getByText(/cắt sát vùng hội thoại/i)).toBeInTheDocument();
    expect(screen.getByText(/che thông tin nhạy cảm/i)).toBeInTheDocument();
  });

  it('rejects files that are not images', async () => {
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    const fileInput = screen.getByLabelText(/tải ảnh chụp đoạn chat/i);
    const invalidFile = new File(['not an image'], 'notes.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, { target: { files: [invalidFile] } });

    expect(screen.getByText(/vui lòng chọn ảnh định dạng png, jpg, jpeg hoặc webp/i)).toBeInTheDocument();
    expect(extractTextFromImage).not.toHaveBeenCalled();
  });

  it('shows a larger preview when a valid image is selected', async () => {
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

  it('extracts text into a review draft before notifying the parent component', async () => {
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
    resolveOcr(createOcrResult('A: Em sao vậy?\nB: Em mệt thôi.'));

    const draft = await screen.findByLabelText(/bản nháp nội dung trích xuất/i);
    expect(draft).toHaveValue('A: Em sao vậy?\nB: Em mệt thôi.');
    expect(onTextExtracted).not.toHaveBeenCalled();
    expect(screen.getAllByText(/đã trích xuất nội dung/i).length).toBeGreaterThanOrEqual(1);

    await user.clear(draft);
    await user.type(draft, 'A: Em sao vậy?\nB: Em mệt thôi.');
    await user.click(screen.getByRole('button', { name: /^dùng nội dung này$/i }));

    expect(onTextExtracted).toHaveBeenCalledWith(
      'A: Em sao vậy?\nB: Em mệt thôi.',
      expect.objectContaining({ text: 'A: Em sao vậy?\nB: Em mệt thôi.' }),
      'replace'
    );
  });

  it('can append reviewed OCR draft when current chat already has content', async () => {
    const user = userEvent.setup();
    const onTextExtracted = vi.fn();
    const result = createOcrResult('A: thêm nội dung OCR');
    vi.mocked(extractTextFromImage).mockResolvedValueOnce(result);

    render(<ImageOcrUploader hasChatText onTextExtracted={onTextExtracted} />);

    await user.upload(
      screen.getByLabelText(/tải ảnh chụp đoạn chat/i),
      new File(['fake image'], 'chat.png', { type: 'image/png' })
    );
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));
    await screen.findByLabelText(/bản nháp nội dung trích xuất/i);
    await user.click(screen.getByRole('button', { name: /nối vào cuối đoạn chat hiện tại/i }));

    expect(onTextExtracted).toHaveBeenCalledWith('A: thêm nội dung OCR', result, 'append');
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
    expect(screen.getByText(/độ tin cậy ocr thấp/i)).toBeInTheDocument();
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

  it('requires explicit consent before sending the image to AI Vision', async () => {
    const user = userEvent.setup();
    render(<ImageOcrUploader onTextExtracted={vi.fn()} />);

    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), new File(['fake image'], 'chat.png', {
      type: 'image/png',
    }));
    await user.click(screen.getByLabelText(/dùng ai vision để trích xuất chính xác hơn/i));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(screen.getByText(/cần đồng ý gửi ảnh này đến ai provider/i)).toBeInTheDocument();
    expect(extractChatTextWithVision).not.toHaveBeenCalled();
    expect(extractTextFromImage).not.toHaveBeenCalled();
  });

  it('uses AI Vision when enabled and consented, then waits for review apply', async () => {
    const user = userEvent.setup();
    const onTextExtracted = vi.fn();
    vi.mocked(extractChatTextWithVision).mockResolvedValueOnce({
      text: 'A: anh iu ngủ ngon nhó\nB: yeuemm 🥺',
      confidence: 91,
      warnings: [],
      provider: 'vision',
    });
    render(<ImageOcrUploader onTextExtracted={onTextExtracted} />);

    const file = new File(['fake image'], 'chat.png', { type: 'image/png' });
    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), file);
    await user.click(screen.getByLabelText(/dùng ai vision để trích xuất chính xác hơn/i));
    await user.click(screen.getByLabelText(/tôi đồng ý gửi ảnh này đến ai provider/i));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(await screen.findByText(/ai vision đã trích xuất nội dung/i)).toBeInTheDocument();
    expect(extractChatTextWithVision).toHaveBeenCalledWith(file, true);
    expect(extractTextFromImage).not.toHaveBeenCalled();
    expect(onTextExtracted).not.toHaveBeenCalled();

    await user.click(screen.getByRole('button', { name: /^dùng nội dung này$/i }));
    expect(onTextExtracted).toHaveBeenCalledWith(
      'A: anh iu ngủ ngon nhó\nB: yeuemm 🥺',
      expect.objectContaining({ language: 'vision', confidence: 91 }),
      'replace'
    );
  });

  it('shows the AI Vision unavailable reason and falls back to local OCR', async () => {
    const user = userEvent.setup();
    const onTextExtracted = vi.fn();
    vi.mocked(extractChatTextWithVision).mockRejectedValueOnce(new Error('AI Vision đang tắt trong cấu hình backend.'));
    vi.mocked(extractTextFromImage).mockResolvedValueOnce(createOcrResult('A: local fallback\nB: vẫn kiểm tra lại'));
    render(<ImageOcrUploader onTextExtracted={onTextExtracted} />);

    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), new File(['fake image'], 'chat.png', {
      type: 'image/png',
    }));
    await user.click(screen.getByLabelText(/dùng ai vision để trích xuất chính xác hơn/i));
    await user.click(screen.getByLabelText(/tôi đồng ý gửi ảnh này đến ai provider/i));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect(await screen.findByText(/ai vision đang tắt trong cấu hình backend/i)).toBeInTheDocument();
    expect(screen.getByText(/đã chuyển sang ocr local/i)).toBeInTheDocument();
    expect(extractTextFromImage).toHaveBeenCalled();
    expect(onTextExtracted).not.toHaveBeenCalled();

    await user.click(screen.getByRole('button', { name: /^dùng nội dung này$/i }));
    expect(onTextExtracted).toHaveBeenCalledWith(
      'A: local fallback\nB: vẫn kiểm tra lại',
      expect.objectContaining({ language: 'vie+eng' }),
      'replace'
    );
  });
});
