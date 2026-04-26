-- Migration: Add consent and privacy controls
-- Created: 2026-04-26

ALTER TABLE analysis_sessions
    RENAME COLUMN message TO chat_text;

ALTER TABLE analysis_sessions
    ALTER COLUMN chat_text DROP NOT NULL,
    ADD COLUMN IF NOT EXISTS summary TEXT,
    ADD COLUMN IF NOT EXISTS context_note TEXT,
    ADD COLUMN IF NOT EXISTS warning TEXT,
    ADD COLUMN IF NOT EXISTS save_input BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS save_result BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS consent_type VARCHAR(80) DEFAULT 'analysis_history',
    ADD COLUMN IF NOT EXISTS is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    save_input BOOLEAN NOT NULL DEFAULT FALSE,
    save_result BOOLEAN NOT NULL DEFAULT FALSE,
    consent_type VARCHAR(80) NOT NULL DEFAULT 'analysis_history',
    is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_consent_type UNIQUE (user_id, consent_type)
);

CREATE INDEX IF NOT EXISTS idx_consents_user_id ON consents(user_id);
CREATE INDEX IF NOT EXISTS idx_consents_type ON consents(consent_type);

COMMENT ON TABLE consents IS 'User consent settings for saving analysis results and chat content';
COMMENT ON COLUMN analysis_sessions.chat_text IS 'Original chat text. Must be NULL unless save_input consent is accepted.';
COMMENT ON COLUMN analysis_sessions.save_input IS 'Whether the user explicitly allowed saving original chat text.';
COMMENT ON COLUMN analysis_sessions.save_result IS 'Whether the user allowed saving analysis result.';
COMMENT ON COLUMN analysis_sessions.consent_type IS 'Consent category used when saving this record.';
COMMENT ON COLUMN analysis_sessions.is_accepted IS 'Whether consent was accepted when this record was saved.';
COMMENT ON COLUMN analysis_sessions.accepted_at IS 'Timestamp when consent was accepted.';
