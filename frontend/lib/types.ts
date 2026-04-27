export interface AnalyzeRequest {
  chat_text: string;
  profile_context: string;
  save_input: boolean;
  save_result: boolean;
}

export interface EvidenceItem {
  quote: string;
  label: string;
  reason: string;
}

export interface AnalyzeResponse {
  overall_emotion: string;
  confidence: number;
  emotion_distribution: Record<string, number>;
  summary: string;
  context_note: string;
  suggested_reply: string;
  warning: string;
  tone?: string | null;
  evidence?: EvidenceItem[];
  uncertainty_reasons?: string[];
  input_quality?: 'good' | 'medium' | 'low' | string;
  reply_style?: string | null;
  authenticated?: boolean;
  saved_to_history?: boolean;
}

export interface VisionOcrResponse {
  text: string;
  confidence: number;
  warnings: string[];
  provider: string;
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
  uid?: string;
  email: string;
  name?: string | null;
  picture?: string | null;
  is_active: boolean;
}
