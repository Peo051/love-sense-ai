-- Migration: Harden user-scoped persistence rules
-- Created: 2026-04-27
-- Target: PostgreSQL 14+ / Supabase

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

ALTER TABLE preferences
    ADD COLUMN IF NOT EXISTS theme VARCHAR(20) NOT NULL DEFAULT 'light';

ALTER TABLE preferences
    ALTER COLUMN language SET DEFAULT 'vi',
    ALTER COLUMN language SET NOT NULL,
    ALTER COLUMN notification_enabled SET DEFAULT TRUE,
    ALTER COLUMN notification_enabled SET NOT NULL,
    ALTER COLUMN theme SET DEFAULT 'light',
    ALTER COLUMN theme SET NOT NULL,
    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN created_at SET NOT NULL,
    ALTER COLUMN updated_at SET DEFAULT CURRENT_TIMESTAMP,
    ALTER COLUMN updated_at SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_preferences_user_id ON preferences(user_id);

-- Privacy invariant: original chat text can only exist with explicit save_input consent.
UPDATE analysis_sessions
SET chat_text = NULL
WHERE chat_text IS NOT NULL
  AND (save_input IS NOT TRUE OR is_accepted IS NOT TRUE);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_analysis_sessions_chat_text_requires_consent'
    ) THEN
        ALTER TABLE analysis_sessions
            ADD CONSTRAINT ck_analysis_sessions_chat_text_requires_consent
            CHECK (chat_text IS NULL OR (save_input IS TRUE AND is_accepted IS TRUE));
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_analysis_sessions_confidence_range'
    ) THEN
        ALTER TABLE analysis_sessions
            ADD CONSTRAINT ck_analysis_sessions_confidence_range
            CHECK (confidence >= 0 AND confidence <= 1);
    END IF;
END $$;

COMMENT ON TABLE preferences IS 'Per-user preference settings.';
COMMENT ON COLUMN analysis_sessions.chat_text IS 'Original chat text. Must stay NULL unless save_input consent is accepted.';
