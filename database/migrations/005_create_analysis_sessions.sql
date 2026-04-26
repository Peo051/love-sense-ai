-- Migration: Create analysis_sessions table
-- Created: 2026-04-26

CREATE TABLE IF NOT EXISTS analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    emotion VARCHAR(50) NOT NULL,
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    suggested_reply TEXT,
    emotion_scores JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes
CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX idx_analysis_sessions_emotion ON analysis_sessions(emotion);

-- Create GIN index for JSONB column
CREATE INDEX idx_analysis_sessions_emotion_scores ON analysis_sessions USING GIN (emotion_scores);

-- Add comment
COMMENT ON TABLE analysis_sessions IS 'History of emotion analysis sessions';
COMMENT ON COLUMN analysis_sessions.emotion_scores IS 'JSON array of all emotion scores';
COMMENT ON COLUMN analysis_sessions.confidence IS 'Confidence score between 0 and 1';
