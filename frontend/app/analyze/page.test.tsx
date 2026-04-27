import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { extractTextFromImage, type OcrExtractionResult } from '@/lib/ocr';
import AnalyzePage from './page';

vi.mock('@/lib/ocr', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/ocr')>();

  return {
    ...actual,
    extractTextFromImage: vi.fn(),
  };
});

const mockAnalyzeResponse = {
  overall_emotion: 'mệt mỏi / né tránh nhẹ',
  confidence: 0.72,
  emotion_distribution: {
    'mệt_mỏi': 0.35,
    'né_tránh': 0.25,
    buồn: 0.2,
    'trung_lập': 0.2,
  },
  summary:
    'Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều. Không đủ dữ liệu để kết luận chắc chắn cảm xúc thật sự.',
  context_note: 'Nếu người này thường im lặng khi mệt, nên phản hồi nhẹ nhàng thay vì hỏi dồn.',
  suggested_reply: 'Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.',
  warning: 'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.',
  tone: 'mệt mỏi / cần khoảng lặng',
  evidence: [
    {
      quote: 'B: Em mệt thôi.',
      label: 'mệt mỏi / né tránh nhẹ',
      reason: 'Câu cho thấy người nói mệt hoặc muốn lùi lại khỏi cuộc trò chuyện lúc đó.',
    },
  ],
  uncertainty_reasons: ['Chỉ dựa trên vài câu chat nên chưa thể kết luận chắc chắn.'],
  input_quality: 'medium',
  reply_style: 'nhẹ nhàng, cho không gian, không hỏi dồn',
};

function createOcrResult(text: string): OcrExtractionResult {
  return {
    text,
    rawText: text,
    confidence: 88,
    language: 'vie+eng',
    quality: {
      score: 0.92,
      warnings: [],
    },
  };
}

function mockFetchOnce(response: unknown, ok = true) {
  const fetchMock = vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    statusText: ok ? 'OK' : 'Server Error',
    json: vi.fn().mockResolvedValue(response),
  });

  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

describe('AnalyzePage', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    vi.mocked(extractTextFromImage).mockReset();
    window.localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.clearAllMocks();
    vi.restoreAllMocks();
    window.localStorage.clear();
  });

  it('renders the analyze form fields and submit button', () => {
    render(<AnalyzePage />);

    expect(screen.getByLabelText(/đoạn chat cần phân tích/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/bối cảnh cá nhân hóa/i)).toBeInTheDocument();
    expect(screen.getByText(/nhập từ ảnh chụp đoạn chat/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /phân tích/i })).toBeInTheDocument();
  });

  it('reviews OCR draft before filling chat text and then submits the extracted text', async () => {
    const user = userEvent.setup();
    const fetchMock = mockFetchOnce(mockAnalyzeResponse);
    const ocrText = 'A: Em sao vậy?\nB: Em mệt thôi.';
    vi.mocked(extractTextFromImage).mockResolvedValueOnce(createOcrResult(ocrText));
    render(<AnalyzePage />);

    const chatInput = screen.getByLabelText(/đoạn chat cần phân tích/i);
    await user.clear(chatInput);
    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), new File(['fake image'], 'chat.png', {
      type: 'image/png',
    }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect((await screen.findAllByText(/đã trích xuất nội dung/i)).length).toBeGreaterThanOrEqual(1);
    expect(await screen.findByLabelText(/bản nháp nội dung trích xuất/i)).toHaveValue(ocrText);
    expect(fetchMock).not.toHaveBeenCalled();

    await user.click(screen.getByRole('button', { name: /^dùng nội dung này$/i }));
    expect(chatInput).toHaveValue(ocrText);
    expect(fetchMock).not.toHaveBeenCalled();

    await user.click(screen.getByRole('button', { name: /phân tích sắc thái/i }));

    const requestBody = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(requestBody).toEqual(
      expect.objectContaining({
        chat_text: ocrText,
        profile_context: expect.stringContaining('trích xuất từ ảnh OCR'),
        save_input: false,
        save_result: false,
      })
    );
    expect(await screen.findByRole('heading', { name: mockAnalyzeResponse.overall_emotion })).toBeInTheDocument();
  });

  it('lets the user append OCR text instead of replacing existing chat text', async () => {
    const user = userEvent.setup();
    const ocrText = 'A: anh iu ngủ ngon nhó\nB: yeuemm';
    vi.mocked(extractTextFromImage).mockResolvedValueOnce(createOcrResult(ocrText));
    render(<AnalyzePage />);

    const chatInput = screen.getByLabelText(/đoạn chat cần phân tích/i);
    await user.upload(screen.getByLabelText(/tải ảnh chụp đoạn chat/i), new File(['fake image'], 'chat.png', {
      type: 'image/png',
    }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    expect((await screen.findAllByText(/đã trích xuất nội dung/i)).length).toBeGreaterThanOrEqual(1);
    await user.click(screen.getByRole('button', { name: /nối vào cuối đoạn chat hiện tại/i }));

    expect((chatInput as HTMLTextAreaElement).value).toContain('A: Em sao');
    expect((chatInput as HTMLTextAreaElement).value).toContain(ocrText);
  });

  it('does not submit and shows validation when chat text is empty', async () => {
    const user = userEvent.setup();
    const fetchMock = mockFetchOnce(mockAnalyzeResponse);
    render(<AnalyzePage />);

    await user.clear(screen.getByLabelText(/đoạn chat cần phân tích/i));
    await user.click(screen.getByRole('button', { name: /phân tích/i }));

    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.getByText(/vui lòng nhập đoạn chat cần phân tích/i)).toBeInTheDocument();
  });

  it('submits valid chat text, shows loading, then renders the analysis result', async () => {
    const user = userEvent.setup();
    let resolveFetch: (value: Response) => void = () => undefined;
    const fetchPromise = new Promise<Response>((resolve) => {
      resolveFetch = resolve;
    });
    const fetchMock = vi.fn().mockReturnValue(fetchPromise);
    vi.stubGlobal('fetch', fetchMock);
    render(<AnalyzePage />);

    await user.clear(screen.getByLabelText(/đoạn chat cần phân tích/i));
    await user.type(screen.getByLabelText(/đoạn chat cần phân tích/i), 'Em mệt thôi.');
    await user.click(screen.getByRole('button', { name: /phân tích/i }));

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/analyze',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      })
    );
    const requestBody = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(requestBody).toEqual(
      expect.objectContaining({
        chat_text: 'Em mệt thôi.',
        profile_context: expect.any(String),
        save_input: false,
        save_result: false,
      })
    );
    expect(screen.getByRole('button', { name: /đang phân tích/i })).toBeDisabled();

    resolveFetch({
      ok: true,
      status: 200,
      statusText: 'OK',
      json: async () => mockAnalyzeResponse,
    } as Response);

    expect(await screen.findByRole('heading', { name: 'mệt mỏi / né tránh nhẹ' })).toBeInTheDocument();
    expect(screen.getByText('72%')).toBeInTheDocument();
    expect(screen.getAllByText(/gợi ý phản hồi/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/câu làm căn cứ/i)).toBeInTheDocument();
    expect(screen.getByText('B: Em mệt thôi.')).toBeInTheDocument();
    expect(screen.getByText(/điểm cần thận trọng/i)).toBeInTheDocument();
    expect(screen.getByText(mockAnalyzeResponse.suggested_reply)).toBeInTheDocument();
    expect(screen.getByText(/kết quả chỉ mang tính tham khảo/i)).toBeInTheDocument();
  });

  it('sends save_result without save_input when only history checkbox is selected', async () => {
    const user = userEvent.setup();
    const fetchMock = mockFetchOnce(mockAnalyzeResponse);
    render(<AnalyzePage />);

    await user.click(screen.getByLabelText(/lưu kết quả phân tích/i));
    await user.click(screen.getByRole('button', { name: /phân tích/i }));

    const requestBody = JSON.parse(fetchMock.mock.calls[0][1].body);
    expect(requestBody).toEqual(
      expect.objectContaining({
        save_result: true,
        save_input: false,
      })
    );
    expect(await screen.findByRole('heading', { name: mockAnalyzeResponse.overall_emotion })).toBeInTheDocument();
  });

  it('shows a friendly backend error and keeps the user input', async () => {
    const user = userEvent.setup();
    mockFetchOnce({ detail: 'Backend đang bận, vui lòng thử lại sau.' }, false);
    render(<AnalyzePage />);

    const chatInput = screen.getByLabelText(/đoạn chat cần phân tích/i);
    await user.clear(chatInput);
    await user.type(chatInput, 'Tin nhắn hợp lệ nhưng API lỗi.');
    await user.click(screen.getByRole('button', { name: /phân tích/i }));

    expect(await screen.findByText(/backend xử lý thất bại/i)).toBeInTheDocument();
    expect(chatInput).toHaveValue('Tin nhắn hợp lệ nhưng API lỗi.');
  });

  it('shows a friendly network error and keeps the user input', async () => {
    const user = userEvent.setup();
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')));
    render(<AnalyzePage />);

    const chatInput = screen.getByLabelText(/đoạn chat cần phân tích/i);
    await user.clear(chatInput);
    await user.type(chatInput, 'Tin nhắn hợp lệ nhưng backend không kết nối.');
    await user.click(screen.getByRole('button', { name: /phân tích/i }));

    expect(await screen.findByText(/không kết nối được backend/i)).toBeInTheDocument();
    expect(chatInput).toHaveValue('Tin nhắn hợp lệ nhưng backend không kết nối.');
  });
});
