import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import TutorPage from './page';
import { analyzeTutorCode, extractChatTextWithVision, hasAuthToken, requestTutorNextHint, verifyTutorRetry } from '@/lib/api';
import { extractTextFromImage } from '@/lib/ocr';

vi.mock('@/lib/api', () => ({
  analyzeTutorCode: vi.fn(),
  requestTutorNextHint: vi.fn(),
  verifyTutorRetry: vi.fn(),
  extractChatTextWithVision: vi.fn(),
  hasAuthToken: vi.fn(() => false),
}));

vi.mock('@/lib/ocr', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/ocr')>();
  return {
    ...actual,
    extractTextFromImage: vi.fn(),
  };
});

const mockAnalyzeResponse = {
  diagnosis: {
    category: 'logic_error',
    issue_type: 'setter_validation',
    severity: 'warning',
    location: 'Balance set accessor',
    confidence: 0.88,
    evidence: {
      code: 'set { _balance = value; }',
      reason: 'Thuộc tính set chưa có điều kiện kiểm tra giá trị nạp vào > 0',
    },
    knowledge_components: ['csharp.property', 'csharp.validation'],
    possible_misconception: {
      type: 'validation_omission',
      description: 'Sinh viên có thể chưa rõ cách dùng từ khóa value để kiểm tra dữ liệu đầu vào',
      confidence: 0.85,
    },
  },
  knowledge_components: ['csharp.property', 'csharp.validation'],
  possible_misconception: {
    type: 'validation_omission',
    description: 'Sinh viên có thể chưa rõ cách dùng từ khóa value để kiểm tra dữ liệu đầu vào',
    confidence: 0.85,
  },
  evidence: {
    code: 'set { _balance = value; }',
    reason: 'Thuộc tính set chưa có điều kiện kiểm tra giá trị nạp vào > 0',
  },
  teaching_strategy: 'socratic_questioning',
  tutor_response: 'Quan sát khối lệnh set trong thuộc tính Balance: nếu người dùng nạp số tiền âm thì số dư sẽ ra sao?',
  hint_level: 1,
  highest_hint_level_used: 1,
  solution_revealed: false,
  next_action: 'Thêm câu lệnh if kiểm tra value > 0 trước khi gán',
  session_id: 'test-session-123',
  guest_context_token: 'signed-token-abc',
};

const mockNextHintResponse = {
  hint_level: 2,
  highest_hint_level_used: 2,
  tutor_response: 'Trong C#, từ khóa ngầm định value chứa giá trị được truyền vào setter. Bạn có thể dùng if (value <= 0) để phát hiện giá trị không hợp lệ.',
  solution_revealed: false,
  next_action: 'Thử viết câu lệnh if (value <= 0) ném ngoại lệ ArgumentException',
  teaching_strategy: 'conceptual_explanation',
  session_id: 'test-session-123',
  guest_context_token: 'signed-token-xyz',
};

const mockVerifyResponse = {
  status: 'likely_resolved',
  resolved: true,
  remaining_issues: [],
  new_issues: [],
  feedback: 'Mã nguồn đã kiểm tra chặt chẽ giá trị nạp vào của thuộc tính Balance.',
  next_action: 'Chúc mừng bạn đã hoàn thành bài tập!',
  disclaimer: 'Lưu ý: Kết quả xác minh được đánh giá qua phân tích tĩnh và AI, không thực thi mã trực tiếp trên hệ thống.',
};

describe('TutorPage (Workspace & Multi-turn Session)', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(hasAuthToken).mockReturnValue(false);
  });

  it('renders all V1 input fields and initial guidance', () => {
    render(<TutorPage />);

    expect(screen.getByRole('heading', { name: /không gian gia sư lập trình c# oop/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/đề bài bài tập/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/mã nguồn c# của bạn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/thông báo lỗi biên dịch/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/câu hỏi \/ băn khoăn của bạn/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/chủ đề oop trọng tâm/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /phân tích mã nguồn/i })).toBeInTheDocument();

    // Ban đầu khi chưa có kết quả, hiển thị thẻ giải thích Socratic 4 cấp độ
    expect(screen.getByRole('heading', { name: /tiến trình gợi ý socratic 4 cấp độ/i })).toBeInTheDocument();
  });

  it('maintains 3 visibly distinct regions: problem, current code, tutor conversation', () => {
    render(<TutorPage />);

    // 3 distinct pedagogical regions
    expect(screen.getByRole('region', { name: /khu vực đề bài/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /khu vực mã nguồn/i })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: /khu vực đối thoại gia sư/i })).toBeInTheDocument();
  });

  it('allows typing, handles Tab indentation, and toggles OCR tab', async () => {
    const user = userEvent.setup();
    render(<TutorPage />);

    const problemInput = screen.getByLabelText(/đề bài bài tập/i);
    fireEvent.change(problemInput, { target: { value: 'Tạo lớp BankAccount có Balance' } });
    expect(problemInput).toHaveValue('Tạo lớp BankAccount có Balance');

    const codeInput = screen.getByLabelText(/mã nguồn c# của bạn/i);
    fireEvent.change(codeInput, { target: { value: 'class BankAccount {' } });
    expect(codeInput).toHaveValue('class BankAccount {');

    // Test Tab key indentation
    fireEvent.keyDown(codeInput, { key: 'Tab' });
    expect(codeInput).toHaveValue('class BankAccount {    ');

    // Test switch to OCR tab
    const ocrTabBtn = screen.getByRole('button', { name: /quét từ ảnh bài tập/i });
    await user.click(ocrTabBtn);
    expect(screen.getByRole('heading', { name: /quét mã nguồn từ ảnh bài tập/i })).toBeInTheDocument();
  });

  it('performs full analyze workflow and displays calibrated confidence without false percentage certainty', async () => {
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);
    const user = userEvent.setup();
    render(<TutorPage />);

    const problemInput = screen.getByLabelText(/đề bài bài tập/i);
    const codeInput = screen.getByLabelText(/mã nguồn c# của bạn/i);

    fireEvent.change(problemInput, { target: { value: 'Tạo lớp BankAccount với thuộc tính Balance kiểm tra số tiền > 0' } });
    fireEvent.change(codeInput, { target: { value: 'public class BankAccount { private decimal _balance; public decimal Balance { get { return _balance; } set { _balance = value; } } }' } });

    const analyzeBtn = screen.getByRole('button', { name: /phân tích mã nguồn/i });
    await user.click(analyzeBtn);

    await waitFor(() => {
      expect(analyzeTutorCode).toHaveBeenCalledTimes(1);
    });

    // 1. Kiểm tra kết quả chẩn đoán kỹ thuật
    expect(await screen.findByRole('heading', { name: /chẩn đoán sư phạm/i })).toBeInTheDocument();
    expect(screen.getByText(/sai lệch logic xử lý hoặc trạng thái/i)).toBeInTheDocument();
    expect(screen.getByText(/vị trí: balance set accessor/i)).toBeInTheDocument();

    // 2. Calibrated Confidence: không được hiển thị con số phần trăm giả tạo
    expect(screen.getByText(/phát hiện có căn cứ rõ ràng/i)).toBeInTheDocument();
    expect(screen.queryByText(/88%/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/0\.88/i)).not.toBeInTheDocument();

    // 3. Knowledge components
    expect(screen.getByText('csharp.property')).toBeInTheDocument();
    expect(screen.getByText('csharp.validation')).toBeInTheDocument();

    // 4. Code Evidence & Misconception
    expect(screen.getByText('set { _balance = value; }')).toBeInTheDocument();
    expect(screen.getByText(/thuộc tính set chưa có điều kiện kiểm tra/i)).toBeInTheDocument();
    expect(screen.getByText(/sinh viên có thể chưa rõ cách dùng từ khóa value/i)).toBeInTheDocument();

    // 5. Tutor response & Level 1 hint
    expect(screen.getByText(/quan sát khối lệnh set trong thuộc tính balance/i)).toBeInTheDocument();
    expect(screen.getByText(/bước tiếp theo: thêm câu lệnh if/i)).toBeInTheDocument();
    expect(screen.getByText(/cấp 1 \/ 4/i)).toBeInTheDocument();
  });

  it('advances to Next Hint (Level 2) when Next Hint button is clicked', async () => {
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);
    vi.mocked(requestTutorNextHint).mockResolvedValueOnce(mockNextHintResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class BankAccount' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class BankAccount {}' } });

    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));
    await screen.findByRole('heading', { name: /chẩn đoán sư phạm/i });

    // Click Next Hint button
    const nextHintBtn = await screen.findByRole('button', { name: /yêu cầu gợi ý tiếp theo/i });
    await user.click(nextHintBtn);

    await waitFor(() => {
      expect(requestTutorNextHint).toHaveBeenCalledWith(
        expect.objectContaining({
          current_hint_level: 1,
          session_id: 'test-session-123',
        })
      );
    });

    // Nội dung gợi ý cập nhật lên Level 2
    expect(await screen.findByText(/trong c#, từ khóa ngầm định value chứa giá trị/i)).toBeInTheDocument();
    expect(screen.getByText(/cấp 2 \/ 4/i)).toBeInTheDocument();
  });

  it('submits revised code in Retry/Verify area and displays verification feedback & disclaimer', async () => {
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);
    vi.mocked(verifyTutorRetry).mockResolvedValueOnce(mockVerifyResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class BankAccount' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class BankAccount {}' } });

    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));
    await screen.findByRole('heading', { name: /chẩn đoán sư phạm/i });

    // Kiểm tra khu vực Retry & Verify
    expect(screen.getByRole('heading', { name: /sửa lại & xác minh/i })).toBeInTheDocument();

    const revisedInput = screen.getByLabelText(/mã nguồn sau khi sửa đổi/i);
    fireEvent.change(revisedInput, {
      target: { value: 'public class BankAccount { set { if (value > 0) _balance = value; } }' },
    });

    const verifyBtn = screen.getByRole('button', { name: /xác minh lần thử lại/i });
    await user.click(verifyBtn);

    await waitFor(() => {
      expect(verifyTutorRetry).toHaveBeenCalledTimes(1);
    });

    expect(await screen.findByText(/mã nguồn đã kiểm tra chặt chẽ giá trị nạp vào/i)).toBeInTheDocument();
    expect(screen.getByText(/likely_resolved/i)).toBeInTheDocument();
    expect(screen.getByText(/không thực thi mã trực tiếp trên hệ thống/i)).toBeInTheDocument();
  });

  it('completes multi-turn cycle (analyze -> hint -> retry -> verify) in a single session without page reload', async () => {
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);
    vi.mocked(requestTutorNextHint).mockResolvedValueOnce(mockNextHintResponse as any);
    vi.mocked(verifyTutorRetry).mockResolvedValueOnce(mockVerifyResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    // 1. Analyze
    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Bài toán BankAccount' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'public class BankAccount {}' } });
    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    expect(await screen.findByRole('heading', { name: /chẩn đoán sư phạm/i })).toBeInTheDocument();

    // 2. Next Hint
    const nextHintBtn = await screen.findByRole('button', { name: /yêu cầu gợi ý tiếp theo/i });
    await user.click(nextHintBtn);
    expect(await screen.findByText(/trong c#, từ khóa ngầm định value/i)).toBeInTheDocument();

    // 3. Retry
    const revisedInput = screen.getByLabelText(/mã nguồn sau khi sửa đổi/i);
    fireEvent.change(revisedInput, { target: { value: 'public class BankAccount { set { if (value > 0) _balance = value; } }' } });

    // 4. Verify
    const verifyBtn = screen.getByRole('button', { name: /xác minh lần thử lại/i });
    await user.click(verifyBtn);

    expect(await screen.findByText(/mã nguồn đã kiểm tra chặt chẽ giá trị nạp vào/i)).toBeInTheDocument();
    expect(screen.getByText(/sinh viên đã chỉnh sửa và gửi lại mã nguồn để xác minh/i)).toBeInTheDocument();
    expect(screen.getByText(/kết quả xác minh lần thử/i)).toBeInTheDocument();
  });

  it('allows starting a new attempt without losing saved previous sessions or turns', async () => {
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);
    const user = userEvent.setup();
    render(<TutorPage />);

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class Person' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class Person {}' } });
    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    expect(await screen.findByRole('heading', { name: /chẩn đoán sư phạm/i })).toBeInTheDocument();
    expect(screen.getAllByText(/lần thử #1/i).length).toBeGreaterThan(0);

    // Click "Bắt đầu lần thử mới (New Attempt)"
    const newAttemptBtn = screen.getByRole('button', { name: /bắt đầu lần thử mới/i });
    await user.click(newAttemptBtn);

    // Lần thử được tăng lên #2
    expect(screen.getAllByText(/lần thử #2/i).length).toBeGreaterThan(0);
    // Lịch sử lần thử cũ được lưu lại
    expect(screen.getByText(/lịch sử các lần thử trước/i)).toBeInTheDocument();
    expect(screen.getAllByText(/lần thử #1/i).length).toBeGreaterThan(0);
    // Timeline vẫn giữ lượt của lần thử trước
    expect(screen.getByText(/bắt đầu lần thử mới #2 cho bài toán hiện tại/i)).toBeInTheDocument();
  });

  it('handles guest mode clearly and avoids persisting guest sessions to database', async () => {
    vi.mocked(hasAuthToken).mockReturnValue(false);
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    // Hiển thị rõ ràng huy hiệu Chế độ Khách
    expect(screen.getByText(/chế độ khách \(không lưu trữ db\)/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class Car' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class Car {}' } });
    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    await waitFor(() => {
      expect(analyzeTutorCode).toHaveBeenCalledWith(
        expect.objectContaining({
          save_input: false,
          save_result: false,
        })
      );
    });
  });

  it('handles authenticated mode clearly and passes consent flags for persistence', async () => {
    vi.mocked(hasAuthToken).mockReturnValue(true);
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    // Hiển thị rõ ràng huy hiệu Đã đăng nhập
    expect(screen.getByText(/đã đăng nhập \(đồng bộ đám mây\)/i)).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class Book' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class Book {}' } });
    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    await waitFor(() => {
      expect(analyzeTutorCode).toHaveBeenCalledWith(
        expect.objectContaining({
          save_input: true,
          save_result: true,
        })
      );
    });
  });

  it('displays clear error message when API fails', async () => {
    vi.mocked(analyzeTutorCode).mockRejectedValueOnce(new Error('Backend đang quá tải. Vui lòng thử lại sau.'));

    const user = userEvent.setup();
    render(<TutorPage />);

    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Đề bài mẫu' } });
    fireEvent.change(screen.getByLabelText(/mã nguồn c# của bạn/i), { target: { value: 'class A {}' } });

    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    expect(await screen.findByText(/backend đang quá tải\. vui lòng thử lại sau\./i)).toBeInTheDocument();
  });

  it('supports full flow: screenshot -> extracted draft -> user review -> populate editor without auto-submitting -> tutor analysis', async () => {
    vi.mocked(extractTextFromImage).mockResolvedValueOnce({
      text: 'public class Car { private string _model; }',
      rawText: 'public class Car { private string _model; }',
      confidence: 90,
      language: 'vie+eng',
      quality: { score: 0.9, warnings: [] },
    });
    vi.mocked(analyzeTutorCode).mockResolvedValueOnce(mockAnalyzeResponse as any);

    const user = userEvent.setup();
    render(<TutorPage />);

    // 1. Switch to OCR tab
    await user.click(screen.getByRole('button', { name: /quét từ ảnh bài tập/i }));

    // 2. Upload image and extract
    const fileInput = screen.getByLabelText(/tải ảnh chụp bài tập/i);
    await user.upload(fileInput, new File(['fake code image'], 'code.png', { type: 'image/png' }));
    await user.click(screen.getByRole('button', { name: /trích xuất chữ từ ảnh/i }));

    // 3. Review and edit draft
    const draft = await screen.findByLabelText(/bản nháp nội dung trích xuất/i);
    expect(draft).toHaveValue('public class Car { private string _model; }');

    fireEvent.change(draft, { target: { value: 'public class Car { public string Model { get; set; } }' } });

    // 4. Apply to editor without submitting
    await user.click(screen.getByRole('button', { name: /^dùng nội dung này$/i }));

    expect(analyzeTutorCode).not.toHaveBeenCalled();
    const codeEditor = screen.getByLabelText(/mã nguồn c# của bạn/i);
    expect(codeEditor).toHaveValue('public class Car { public string Model { get; set; } }');

    // 5. Fill problem statement and submit analysis explicitly
    fireEvent.change(screen.getByLabelText(/đề bài bài tập/i), { target: { value: 'Tạo class Car với property Model' } });
    await user.click(screen.getByRole('button', { name: /phân tích mã nguồn/i }));

    await waitFor(() => {
      expect(analyzeTutorCode).toHaveBeenCalledWith(
        expect.objectContaining({
          student_code: 'public class Car { public string Model { get; set; } }',
          problem_statement: 'Tạo class Car với property Model',
        })
      );
    });
    expect(await screen.findByText('Quan sát khối lệnh set trong thuộc tính Balance: nếu người dùng nạp số tiền âm thì số dư sẽ ra sao?')).toBeInTheDocument();
  });
});
