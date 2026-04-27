import type {
  AnalyzeRequest,
  AnalyzeResponse,
  AuthToken,
  AuthUser,
  ConsentSettings,
  HistoryItem,
  HistoryListResponse,
  ProfilePayload,
  ProfileResponse,
} from './types';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  'http://127.0.0.1:8000';
const AUTH_TOKEN_KEY = 'love_emotion_auth_token';
const SAFE_ANALYZE_WARNING = 'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.';

if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
  console.log('[API] Base URL:', API_BASE_URL);
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

function buildHeaders(init?: RequestInit) {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
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
    throw new Error(getErrorMessage(payload, fallbackMessage));
  }

  if (payload === null) {
    throw new Error(fallbackMessage);
  }

  return payload as T;
}

async function requestJson<T>(path: string, init?: RequestInit, fallbackMessage = 'Không thể xử lý yêu cầu.') {
  try {
    const url = `${API_BASE_URL}${path}`;

    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      console.log('[API] Request:', init?.method || 'GET', url);
    }

    const response = await fetch(url, {
      ...init,
      headers: buildHeaders(init),
    });

    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      console.log('[API] Response:', response.status, response.statusText);
    }

    return parseJsonResponse<T>(response, fallbackMessage);
  } catch (error) {
    if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
      console.error('[API] Error:', error);
    }

    if (error instanceof Error) {
      throw error;
    }
    throw new Error(fallbackMessage);
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

function normalizeAnalyzeResponse(value: unknown): AnalyzeResponse {
  const data = isRecord(value) ? value : {};
  const confidence = typeof data.confidence === 'number' && Number.isFinite(data.confidence) ? data.confidence : 0;

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
        : 'Mình có thể nói chuyện thêm khi em sẵn sàng nhé.',
    warning:
      typeof data.warning === 'string' && data.warning.trim()
        ? data.warning
        : SAFE_ANALYZE_WARNING,
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

  const response = await fetch(`${API_BASE_URL}/api/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  const token = await parseJsonResponse<AuthToken>(response, 'Không thể đăng nhập.');
  saveAuthToken(token.access_token);
  return token;
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
