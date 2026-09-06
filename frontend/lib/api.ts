import type {
  AnalyzeRequest,
  AnalyzeResponse,
  AttemptCreateRequest,
  AuthToken,
  AuthUser,
  ConsentSettings,
  EvidenceItem,
  HistoryItem,
  HistoryListResponse,
  LearningSessionDetail,
  LearningSessionSummary,
  MessageCreateRequest,
  ProfilePayload,
  ProfileResponse,
  SessionCreateRequest,
  StudentAttemptResponse,
  StudentProgressDashboardResponse,
  TutorHintRequest,
  TutorHintResponse,
  TutorMessageResponse,
  TutorRequest,
  TutorResponse,
  TutorVerifyRequest,
  TutorVerifyResponse,
  VisionOcrResponse,
} from './types';

const DEFAULT_LOCAL_API_BASE_URL = 'http://127.0.0.1:8000';
const API_REQUEST_TIMEOUT_MS = 60_000;
const MISSING_API_BASE_URL_MESSAGE = 'Missing NEXT_PUBLIC_API_BASE_URL';
const NETWORK_ERROR_MESSAGE = 'Không kết nối được backend. Vui lòng kiểm tra cấu hình API hoặc thử lại sau.';
const TIMEOUT_ERROR_MESSAGE = 'Backend phản hồi quá lâu, vui lòng thử lại.';
const BACKEND_ERROR_MESSAGE = 'Backend xử lý thất bại. Vui lòng thử lại sau.';
const UNAUTHORIZED_ERROR_MESSAGE = 'Bạn cần đăng nhập để thực hiện thao tác này.';
const API_BASE_URL = resolveApiBaseUrl();
const AUTH_TOKEN_KEY = 'love_emotion_auth_token';
const SAFE_ANALYZE_WARNING = 'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.';
let authTokenProvider: (() => Promise<string | null>) | null = null;

class ApiRequestError extends Error {
  status?: number;
  code?: 'config' | 'network' | 'timeout' | 'http';

  constructor(message: string, options?: { status?: number; code?: ApiRequestError['code'] }) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = options?.status;
    this.code = options?.code;
  }
}

function resolveApiBaseUrl() {
  const configuredBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || '';
  const normalizedBaseUrl = configuredBaseUrl.trim().replace(/\/+$/, '');

  if (normalizedBaseUrl) {
    return normalizedBaseUrl;
  }

  if (process.env.NODE_ENV === 'production') {
    return '';
  }

  return DEFAULT_LOCAL_API_BASE_URL;
}

if (process.env.NODE_ENV !== 'production' && process.env.NODE_ENV !== 'test') {
  console.info('[API] base URL', API_BASE_URL || MISSING_API_BASE_URL_MESSAGE);
}

function buildApiUrl(path: string) {
  if (!API_BASE_URL) {
    throw new ApiRequestError(MISSING_API_BASE_URL_MESSAGE, { code: 'config' });
  }

  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function getStoredToken() {
  if (typeof window === 'undefined') {
    return null;
  }
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthTokenProvider(provider: (() => Promise<string | null>) | null) {
  authTokenProvider = provider;
}

export function saveAuthToken(token: string) {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(AUTH_TOKEN_KEY, token);
  }
}

export function clearAuthToken() {
  if (typeof window !== 'undefined') {
    window.localStorage.removeItem(AUTH_TOKEN_KEY);
  }
}

export function hasAuthToken() {
  return Boolean(getStoredToken());
}

async function getRequestToken() {
  if (authTokenProvider) {
    try {
      const token = await authTokenProvider();
      if (token) {
        return token;
      }
    } catch {
      return getStoredToken();
    }
  }
  return getStoredToken();
}

async function buildHeaders(init?: RequestInit) {
  const token = await getRequestToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(init?.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function buildAuthHeaders(init?: RequestInit) {
  const token = await getRequestToken();
  const headers: Record<string, string> = {
    ...(init?.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function readResponsePayload(response: Response): Promise<unknown> {
  if (typeof response.text === 'function') {
    const text = await response.text();
    if (!text) {
      return null;
    }

    try {
      return JSON.parse(text);
    } catch {
      return { rawText: text };
    }
  }

  if (typeof response.json === 'function') {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  return null;
}

function getErrorMessage(payload: unknown, fallbackMessage: string) {
  if (isRecord(payload)) {
    if (typeof payload.detail === 'string') {
      return payload.detail;
    }
    if (typeof payload.message === 'string') {
      return payload.message;
    }
    if (typeof payload.rawText === 'string' && payload.rawText.trim()) {
      return payload.rawText;
    }
  }

  return fallbackMessage;
}

async function parseJsonResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  const payload = await readResponsePayload(response);

  if (!response.ok) {
    throw new ApiRequestError(getHttpErrorMessage(response, payload, fallbackMessage), {
      status: response.status,
      code: 'http',
    });
  }

  if (payload === null) {
    throw new Error(fallbackMessage);
  }

  return payload as T;
}

function getHttpErrorMessage(response: Response, payload: unknown, fallbackMessage: string) {
  if (response.status === 401) {
    return UNAUTHORIZED_ERROR_MESSAGE;
  }

  if (response.status === 408 || response.status === 504) {
    return TIMEOUT_ERROR_MESSAGE;
  }

  if (response.status >= 500) {
    return BACKEND_ERROR_MESSAGE;
  }

  return getErrorMessage(payload, fallbackMessage);
}

async function fetchWithTimeout(url: string, init?: RequestInit) {
  const controller = new AbortController();
  const timeoutId = globalThis.setTimeout(() => controller.abort(), API_REQUEST_TIMEOUT_MS);

  try {
    return await fetch(url, {
      ...init,
      signal: init?.signal ?? controller.signal,
    });
  } finally {
    globalThis.clearTimeout(timeoutId);
  }
}

function toApiError(error: unknown, fallbackMessage: string) {
  if (error instanceof ApiRequestError) {
    return error;
  }

  if (error instanceof Error) {
    if (error.name === 'AbortError') {
      return new ApiRequestError(TIMEOUT_ERROR_MESSAGE, { code: 'timeout' });
    }

    if (error instanceof TypeError && /failed to fetch|networkerror|load failed/i.test(error.message)) {
      return new ApiRequestError(NETWORK_ERROR_MESSAGE, { code: 'network' });
    }

    return error;
  }

  return new Error(fallbackMessage);
}

async function requestJson<T>(path: string, init?: RequestInit, fallbackMessage = 'Không thể xử lý yêu cầu.') {
  try {
    const url = buildApiUrl(path);

    const response = await fetchWithTimeout(url, {
      ...init,
      headers: await buildHeaders(init),
    });

    return parseJsonResponse<T>(response, fallbackMessage);
  } catch (error) {
    throw toApiError(error, fallbackMessage);
  }
}

async function requestFormData<T>(path: string, formData: FormData, fallbackMessage: string) {
  try {
    const response = await fetchWithTimeout(buildApiUrl(path), {
      method: 'POST',
      headers: await buildAuthHeaders(),
      body: formData,
    });

    return parseJsonResponse<T>(response, fallbackMessage);
  } catch (error) {
    throw toApiError(error, fallbackMessage);
  }
}

function normalizeEmotionDistribution(value: unknown): Record<string, number> {
  if (!isRecord(value)) {
    return { trung_lap: 1 };
  }

  const distribution = Object.entries(value).reduce<Record<string, number>>((current, [emotion, score]) => {
    current[emotion] = typeof score === 'number' && Number.isFinite(score) ? score : 0;
    return current;
  }, {});

  return Object.keys(distribution).length > 0 ? distribution : { trung_lap: 1 };
}

function normalizeStringList(value: unknown, limit = 4): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .filter((item): item is string => typeof item === 'string')
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, limit);
}

function normalizeEvidenceList(value: unknown, limit = 4): EvidenceItem[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => {
      if (typeof item === 'string') {
        const quote = item.trim();
        return quote
          ? {
              quote,
              label: 'tín hiệu hội thoại',
              reason: 'Câu này được dùng làm căn cứ tham khảo cho phân tích.',
            }
          : null;
      }

      if (isRecord(item) && typeof item.quote === 'string' && item.quote.trim()) {
        return {
          quote: item.quote.trim(),
          label: typeof item.label === 'string' && item.label.trim() ? item.label.trim() : 'tín hiệu hội thoại',
          reason:
            typeof item.reason === 'string' && item.reason.trim()
              ? item.reason.trim()
              : 'Câu này được dùng làm căn cứ tham khảo cho phân tích.',
        };
      }

      return null;
    })
    .filter((item): item is EvidenceItem => item !== null)
    .slice(0, limit);
}

function normalizeAnalyzeResponse(value: unknown): AnalyzeResponse {
  const data = isRecord(value) ? value : {};
  const confidence = typeof data.confidence === 'number' && Number.isFinite(data.confidence) ? data.confidence : 0;
  const inputQuality = typeof data.input_quality === 'string' && data.input_quality.trim() ? data.input_quality : 'medium';

  return {
    overall_emotion:
      typeof data.overall_emotion === 'string' && data.overall_emotion.trim()
        ? data.overall_emotion
        : 'trung lập / chưa đủ dữ liệu',
    confidence: Math.min(1, Math.max(0, confidence)),
    emotion_distribution: normalizeEmotionDistribution(data.emotion_distribution),
    summary:
      typeof data.summary === 'string' && data.summary.trim()
        ? data.summary
        : 'Backend chưa trả tóm tắt đầy đủ. Kết quả chỉ nên dùng để tham khảo.',
    context_note:
      typeof data.context_note === 'string' && data.context_note.trim()
        ? data.context_note
        : 'Chưa có ghi chú bối cảnh bổ sung.',
    suggested_reply:
      typeof data.suggested_reply === 'string' && data.suggested_reply.trim()
        ? data.suggested_reply
        : 'Mình có thể nói chuyện thêm khi bạn sẵn sàng.',
    warning:
      typeof data.warning === 'string' && data.warning.trim()
        ? data.warning
        : SAFE_ANALYZE_WARNING,
    tone: typeof data.tone === 'string' && data.tone.trim() ? data.tone : null,
    evidence: normalizeEvidenceList(data.evidence),
    uncertainty_reasons: normalizeStringList(data.uncertainty_reasons),
    input_quality: inputQuality,
    reply_style: typeof data.reply_style === 'string' && data.reply_style.trim() ? data.reply_style : null,
    authenticated: typeof data.authenticated === 'boolean' ? data.authenticated : false,
    saved_to_history: typeof data.saved_to_history === 'boolean' ? data.saved_to_history : false,
  };
}

export async function registerUser(email: string, password: string): Promise<AuthUser> {
  return requestJson<AuthUser>(
    '/api/register',
    {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    },
    'Không thể đăng ký tài khoản.'
  );
}

export async function loginUser(email: string, password: string): Promise<AuthToken> {
  const formData = new URLSearchParams();
  formData.set('username', email);
  formData.set('password', password);

  try {
    const response = await fetchWithTimeout(buildApiUrl('/api/token'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData,
    });

    const token = await parseJsonResponse<AuthToken>(response, 'Không thể đăng nhập.');
    saveAuthToken(token.access_token);
    return token;
  } catch (error) {
    throw toApiError(error, 'Không thể đăng nhập.');
  }
}

export async function getCurrentUser(): Promise<AuthUser> {
  return requestJson<AuthUser>('/api/me', undefined, 'Không thể tải thông tin tài khoản.');
}

export async function analyzeEmotion(payload: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await requestJson<unknown>(
    '/api/analyze',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể phân tích đoạn chat lúc này.'
  );
  return normalizeAnalyzeResponse(response);
}

export async function extractChatTextWithVision(file: File, isAccepted: boolean): Promise<VisionOcrResponse> {
  const formData = new FormData();
  formData.set('image', file);
  formData.set('is_accepted', String(isAccepted));

  return requestFormData<VisionOcrResponse>(
    '/api/ocr/vision',
    formData,
    'Không thể dùng AI Vision lúc này. Vui lòng dùng OCR local hoặc nhập thủ công.'
  );
}

export async function getProfile(): Promise<ProfileResponse> {
  return requestJson<ProfileResponse>('/api/profile', undefined, 'Vui lòng đăng nhập để tải hồ sơ.');
}

export async function saveProfile(profile: ProfilePayload): Promise<ProfileResponse> {
  return requestJson<ProfileResponse>(
    '/api/profile',
    {
      method: 'POST',
      body: JSON.stringify(profile),
    },
    'Vui lòng đăng nhập để lưu hồ sơ.'
  );
}

export async function deleteProfile(): Promise<void> {
  await requestJson<{ deleted: boolean }>('/api/profile', { method: 'DELETE' }, 'Không thể xóa hồ sơ.');
}

export async function getHistory(): Promise<HistoryListResponse> {
  return requestJson<HistoryListResponse>('/api/history', undefined, 'Vui lòng đăng nhập để tải lịch sử phân tích.');
}

export async function getHistoryDetail(id: string): Promise<HistoryItem> {
  return requestJson<HistoryItem>(`/api/history/${id}`, undefined, 'Không thể tải chi tiết lịch sử.');
}

export async function deleteHistoryItem(id: string): Promise<void> {
  await requestJson<{ deleted: boolean }>(`/api/history/${id}`, { method: 'DELETE' }, 'Không thể xóa lịch sử.');
}

export async function clearHistory(): Promise<void> {
  await requestJson<{ deleted: boolean }>('/api/history', { method: 'DELETE' }, 'Không thể xóa toàn bộ lịch sử.');
}

export async function getConsent(): Promise<ConsentSettings> {
  return requestJson<ConsentSettings>('/api/consent', undefined, 'Vui lòng đăng nhập để tải cài đặt quyền riêng tư.');
}

export async function saveConsent(consent: ConsentSettings): Promise<ConsentSettings> {
  return requestJson<ConsentSettings>(
    '/api/consent',
    {
      method: 'POST',
      body: JSON.stringify(consent),
    },
    'Không thể lưu cài đặt quyền riêng tư.'
  );
}

export async function deleteUserData(): Promise<void> {
  await requestJson<{ deleted: boolean }>('/api/user-data', { method: 'DELETE' }, 'Không thể xóa dữ liệu cá nhân.');
}

export async function analyzeTutorCode(payload: TutorRequest): Promise<TutorResponse> {
  return requestJson<TutorResponse>(
    '/api/tutor/analyze',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể phân tích mã nguồn lúc này. Vui lòng thử lại sau.'
  );
}

export async function requestTutorNextHint(payload: TutorHintRequest): Promise<TutorHintResponse> {
  return requestJson<TutorHintResponse>(
    '/api/tutor/hint',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể lấy gợi ý tiếp theo lúc này. Vui lòng thử lại sau.'
  );
}

export async function verifyTutorRetry(payload: TutorVerifyRequest): Promise<TutorVerifyResponse> {
  return requestJson<TutorVerifyResponse>(
    '/api/tutor/verify',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể xác minh lần thử lại lúc này. Vui lòng thử lại sau.'
  );
}

export async function createLearningSession(payload: SessionCreateRequest): Promise<LearningSessionDetail> {
  return requestJson<LearningSessionDetail>(
    '/api/sessions',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể tạo phiên học tập lúc này.'
  );
}

export async function listLearningSessions(): Promise<LearningSessionSummary[]> {
  return requestJson<LearningSessionSummary[]>(
    '/api/sessions',
    undefined,
    'Không thể tải danh sách phiên học tập.'
  );
}

export async function getLearningSession(sessionId: string): Promise<LearningSessionDetail> {
  return requestJson<LearningSessionDetail>(
    `/api/sessions/${sessionId}`,
    undefined,
    'Không thể tải chi tiết phiên học tập.'
  );
}

export async function deleteLearningSession(sessionId: string): Promise<void> {
  await requestJson<{ deleted: boolean }>(
    `/api/sessions/${sessionId}`,
    { method: 'DELETE' },
    'Không thể xóa phiên học tập.'
  );
}

export async function addSessionAttempt(
  sessionId: string,
  payload: AttemptCreateRequest
): Promise<StudentAttemptResponse> {
  return requestJson<StudentAttemptResponse>(
    `/api/sessions/${sessionId}/attempts`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể lưu lần thử vào phiên học.'
  );
}

export async function addSessionMessage(
  sessionId: string,
  payload: MessageCreateRequest
): Promise<TutorMessageResponse> {
  return requestJson<TutorMessageResponse>(
    `/api/sessions/${sessionId}/messages`,
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể lưu tin nhắn vào phiên học.'
  );
}

export async function getProgressDashboard(): Promise<StudentProgressDashboardResponse> {
  return requestJson<StudentProgressDashboardResponse>(
    '/api/progress/dashboard',
    undefined,
    'Không thể tải dữ liệu tiến độ học tập lúc này.'
  );
}



