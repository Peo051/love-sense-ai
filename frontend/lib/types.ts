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

export type TutorDiagnosisCategory =
  | 'compile_error'
  | 'runtime_error'
  | 'logic_error'
  | 'conceptual_misuse'
  | 'requirement_violation'
  | 'no_bug'
  | 'insufficient_context'
  | 'unknown';

export interface TutorEvidence {
  code: string;
  reason: string;
}

export interface PossibleMisconception {
  type: string;
  description: string;
  confidence: number;
}

export interface TutorDiagnosis {
  category: TutorDiagnosisCategory;
  issue_type: string;
  severity: 'info' | 'warning' | 'error' | string;
  location?: string | null;
  confidence: number;
  evidence?: TutorEvidence | null;
  knowledge_components: string[];
  possible_misconception?: PossibleMisconception | null;
}

export interface TutorRequest {
  problem_statement: string;
  student_code: string;
  programming_language?: string;
  compiler_error?: string | null;
  student_question?: string | null;
  topic?: string | null;
  hint_level?: number;
  save_input?: boolean;
  save_result?: boolean;
}

export interface TutorResponse {
  diagnosis: TutorDiagnosis;
  knowledge_components: string[];
  possible_misconception?: PossibleMisconception | null;
  evidence?: TutorEvidence | null;
  teaching_strategy: string;
  tutor_response: string;
  hint_level: number;
  highest_hint_level_used: number;
  solution_revealed: boolean;
  next_action: string;
  prompt_version?: string;
  session_id?: string | null;
  created_at?: string | null;
  validator_actions?: string[];
  guest_context_token?: string | null;
}

export interface TutorHintRequest {
  session_id?: string | null;
  guest_context_token?: string | null;
  current_hint_level: number;
  current_diagnosis?: TutorDiagnosis | null;
  student_code?: string | null;
  student_followup_message?: string | null;
}

export interface TutorHintResponse {
  hint_level: number;
  highest_hint_level_used: number;
  tutor_response: string;
  solution_revealed: boolean;
  next_action: string;
  teaching_strategy: string;
  session_id?: string | null;
  guest_context_token?: string | null;
}

export type VerificationStatus =
  | 'likely_resolved'
  | 'still_present'
  | 'new_issue'
  | 'needs_execution_to_confirm';

export interface TutorVerifyRequest {
  original_problem: string;
  revised_student_code: string;
  previous_code?: string | null;
  original_diagnosis?: TutorDiagnosis | null;
  session_id?: string | null;
  guest_context_token?: string | null;
}

export interface TutorVerifyResponse {
  status: VerificationStatus;
  resolved: boolean;
  remaining_issues: string[];
  new_issues: string[];
  feedback: string;
  next_action: string;
  disclaimer: string;
  diagnosis?: TutorDiagnosis | null;
}

