-- Migration: Add auth-scoped SQLAlchemy model columns
-- Created: 2026-04-26
-- Target: PostgreSQL 14+ / Supabase

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Profiles now store one profile per authenticated user.
ALTER TABLE profiles
    ADD COLUMN IF NOT EXISTS nickname VARCHAR(80),
    ADD COLUMN IF NOT EXISTS primary_language VARCHAR(80) NOT NULL DEFAULT 'Tiếng Việt',
    ADD COLUMN IF NOT EXISTS communication_style VARCHAR(120) NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS relationship_status VARCHAR(120) NOT NULL DEFAULT '';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'profiles' AND column_name = 'name'
    ) THEN
        UPDATE profiles SET nickname = COALESCE(nickname, name);
        ALTER TABLE profiles DROP COLUMN name;
    END IF;
END $$;

UPDATE profiles SET nickname = COALESCE(nickname, '');
UPDATE profiles SET communication_style = COALESCE(communication_style, '');

ALTER TABLE profiles
    ALTER COLUMN nickname SET NOT NULL,
    ALTER COLUMN nickname SET DEFAULT '',
    ALTER COLUMN communication_style TYPE VARCHAR(120),
    ALTER COLUMN communication_style SET DEFAULT '',
    ALTER COLUMN communication_style SET NOT NULL;

ALTER TABLE profiles DROP COLUMN IF EXISTS age;

CREATE UNIQUE INDEX IF NOT EXISTS uq_profiles_user_id ON profiles(user_id);

-- Partner profile stores the personalization fields used by the frontend.
ALTER TABLE partner_profiles
    ADD COLUMN IF NOT EXISTS nickname VARCHAR(80),
    ADD COLUMN IF NOT EXISTS likes TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS dislikes TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS texting_style TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS when_happy TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS when_sad TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS when_angry TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS likes_checkins BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS dislikes_repeated_questions BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS height_cm DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS weight_kg DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS appearance TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS private_notes TEXT;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'partner_profiles' AND column_name = 'name'
    ) THEN
        UPDATE partner_profiles SET nickname = COALESCE(nickname, name);
        ALTER TABLE partner_profiles DROP COLUMN name;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'partner_profiles' AND column_name = 'notes'
    ) THEN
        UPDATE partner_profiles SET private_notes = COALESCE(private_notes, notes);
        ALTER TABLE partner_profiles DROP COLUMN notes;
    END IF;
END $$;

UPDATE partner_profiles
SET
    nickname = COALESCE(nickname, ''),
    private_notes = COALESCE(private_notes, '');

ALTER TABLE partner_profiles
    ALTER COLUMN nickname SET NOT NULL,
    ALTER COLUMN nickname SET DEFAULT '',
    ALTER COLUMN private_notes SET NOT NULL,
    ALTER COLUMN private_notes SET DEFAULT '';

ALTER TABLE partner_profiles DROP COLUMN IF EXISTS age;

CREATE UNIQUE INDEX IF NOT EXISTS uq_partner_profiles_user_id ON partner_profiles(user_id);

-- Consent adds history_enabled while keeping save_input false by default.
ALTER TABLE consents
    ADD COLUMN IF NOT EXISTS history_enabled BOOLEAN NOT NULL DEFAULT TRUE;

CREATE UNIQUE INDEX IF NOT EXISTS uq_consents_user_type ON consents(user_id, consent_type);

-- Analysis history stores only summarized results unless save_input was explicitly accepted.
ALTER TABLE analysis_sessions
    ADD COLUMN IF NOT EXISTS analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS overall_emotion VARCHAR(120),
    ADD COLUMN IF NOT EXISTS emotion_distribution JSONB,
    ADD COLUMN IF NOT EXISTS summary TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS context_note TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS suggested_reply TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS warning TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS save_input BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS save_result BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS consent_type VARCHAR(80) NOT NULL DEFAULT 'analysis_history',
    ADD COLUMN IF NOT EXISTS is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS accepted_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS chat_text TEXT;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'analysis_sessions' AND column_name = 'message'
    ) THEN
        UPDATE analysis_sessions SET chat_text = COALESCE(chat_text, message);
        ALTER TABLE analysis_sessions DROP COLUMN message;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'analysis_sessions' AND column_name = 'emotion'
    ) THEN
        UPDATE analysis_sessions SET overall_emotion = COALESCE(overall_emotion, emotion);
        ALTER TABLE analysis_sessions DROP COLUMN emotion;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'analysis_sessions' AND column_name = 'emotion_scores'
    ) THEN
        UPDATE analysis_sessions SET emotion_distribution = COALESCE(emotion_distribution, emotion_scores);
        ALTER TABLE analysis_sessions DROP COLUMN emotion_scores;
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'analysis_sessions' AND column_name = 'created_at'
    ) THEN
        UPDATE analysis_sessions SET analyzed_at = COALESCE(analyzed_at, created_at);
        ALTER TABLE analysis_sessions DROP COLUMN created_at;
    END IF;
END $$;

UPDATE analysis_sessions
SET
    analyzed_at = COALESCE(analyzed_at, CURRENT_TIMESTAMP),
    overall_emotion = COALESCE(overall_emotion, 'trung lập'),
    confidence = COALESCE(confidence, 0),
    emotion_distribution = COALESCE(emotion_distribution, '{}'::jsonb),
    summary = COALESCE(summary, ''),
    context_note = COALESCE(context_note, ''),
    suggested_reply = COALESCE(suggested_reply, ''),
    warning = COALESCE(warning, 'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.');

UPDATE analysis_sessions
SET chat_text = NULL
WHERE save_input IS FALSE OR is_accepted IS FALSE;

ALTER TABLE analysis_sessions
    ALTER COLUMN analyzed_at SET NOT NULL,
    ALTER COLUMN overall_emotion SET NOT NULL,
    ALTER COLUMN confidence TYPE DOUBLE PRECISION,
    ALTER COLUMN confidence SET NOT NULL,
    ALTER COLUMN emotion_distribution SET NOT NULL,
    ALTER COLUMN emotion_distribution SET DEFAULT '{}'::jsonb,
    ALTER COLUMN summary SET NOT NULL,
    ALTER COLUMN context_note SET NOT NULL,
    ALTER COLUMN suggested_reply SET NOT NULL,
    ALTER COLUMN warning SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_analysis_sessions_analyzed_at ON analysis_sessions(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_overall_emotion ON analysis_sessions(overall_emotion);
CREATE INDEX IF NOT EXISTS idx_analysis_sessions_emotion_distribution ON analysis_sessions USING GIN (emotion_distribution);

COMMENT ON COLUMN analysis_sessions.chat_text IS 'Original chat text. Must stay NULL unless save_input consent is accepted.';
COMMENT ON COLUMN analysis_sessions.save_input IS 'Whether user explicitly allowed saving original chat text.';
COMMENT ON COLUMN analysis_sessions.save_result IS 'Whether user allowed saving the summarized analysis result.';
