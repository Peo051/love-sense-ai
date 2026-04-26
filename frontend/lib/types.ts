export interface EmotionResult {
  emotion: string;
  confidence: number;
  emotions: EmotionScore[];
  suggestedReplies: string[];
}

export interface EmotionScore {
  name: string;
  value: number;
}

export interface UserProfile {
  name: string;
  age: number;
  communicationStyle: string;
}

export interface PartnerProfile {
  name: string;
  age: number;
}

export interface AnalysisHistory {
  id: string;
  date: string;
  message: string;
  emotion: string;
  confidence: number;
}
