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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AUTH_TOKEN_KEY = 'love_emotion_auth_token';

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

async function parseJsonResponse<T>(response: Response, fallbackMessage: string): Promise<T> {
  if (!response.ok) {
    let message = fallbackMessage;

    try {
      const errorBody = await response.json();
      if (typeof errorBody.detail === 'string') {
        message = errorBody.detail;
      }
    } catch {
      // Giữ thông báo mặc định nếu backend không trả JSON hợp lệ.
    }

    throw new Error(message);
  }

  return response.json();
}

async function requestJson<T>(path: string, init?: RequestInit, fallbackMessage = 'Không thể xử lý yêu cầu.') {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: buildHeaders(init),
  });

  return parseJsonResponse<T>(response, fallbackMessage);
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
  return requestJson<AnalyzeResponse>(
    '/api/analyze',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    'Không thể phân tích đoạn chat lúc này.'
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
