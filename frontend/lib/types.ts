export interface AnalyzeRequest {
  chat_text: string;
  profile_context: string;
  save_input: boolean;
  save_result: boolean;
}

export interface AnalyzeResponse {
  overall_emotion: string;
  confidence: number;
  emotion_distribution: Record<string, number>;
  summary: string;
  context_note: string;
  suggested_reply: string;
  warning: string;
}

export interface UserProfile {
  nickname: string;
  primary_language: string;
  communication_style: string;
  relationship_status: string;
}

export interface PartnerProfile {
  nickname: string;
  likes: string;
  dislikes: string;
  texting_style: string;
  when_happy: string;
  when_sad: string;
  when_angry: string;
  likes_checkins: boolean;
  dislikes_repeated_questions: boolean;
  height_cm?: number | null;
  weight_kg?: number | null;
  appearance: string;
  private_notes: string;
}

export interface ProfilePayload {
  user_profile: UserProfile;
  partner_profile: PartnerProfile;
}

export interface ProfileResponse extends ProfilePayload {
  updated_at: string;
}

export interface ConsentSettings {
  history_enabled: boolean;
  save_input: boolean;
  save_result: boolean;
  consent_type: string;
  is_accepted: boolean;
  accepted_at: string | null;
}

export interface HistoryItem extends AnalyzeResponse {
  id: string;
  analyzed_at: string;
  save_input: boolean;
  save_result: boolean;
  chat_text: string | null;
}

export interface HistoryListResponse {
  items: HistoryItem[];
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface AuthUser {
  id: string;
  email: string;
  is_active: boolean;
}
