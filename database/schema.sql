-- Love Emotion Database Schema
-- Target: PostgreSQL 14+ / Supabase

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

DROP TABLE IF EXISTS analysis_sessions CASCADE;
DROP TABLE IF EXISTS consents CASCADE;
DROP TABLE IF EXISTS preferences CASCADE;
DROP TABLE IF EXISTS partner_profiles CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    nickname VARCHAR(80) NOT NULL DEFAULT '',
    primary_language VARCHAR(80) NOT NULL DEFAULT 'Tiếng Việt',
    communication_style VARCHAR(120) NOT NULL DEFAULT '',
    relationship_status VARCHAR(120) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_user_id ON profiles(user_id);

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE partner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    nickname VARCHAR(80) NOT NULL DEFAULT '',
    likes TEXT NOT NULL DEFAULT '',
    dislikes TEXT NOT NULL DEFAULT '',
    texting_style TEXT NOT NULL DEFAULT '',
    when_happy TEXT NOT NULL DEFAULT '',
    when_sad TEXT NOT NULL DEFAULT '',
    when_angry TEXT NOT NULL DEFAULT '',
    likes_checkins BOOLEAN NOT NULL DEFAULT TRUE,
    dislikes_repeated_questions BOOLEAN NOT NULL DEFAULT TRUE,
    height_cm DOUBLE PRECISION,
    weight_kg DOUBLE PRECISION,
    appearance TEXT NOT NULL DEFAULT '',
    private_notes TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partner_profiles_user_id ON partner_profiles(user_id);

CREATE TRIGGER update_partner_profiles_updated_at
    BEFORE UPDATE ON partner_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'vi',
    notification_enabled BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_preferences_user_id ON preferences(user_id);

CREATE TRIGGER update_preferences_updated_at
    BEFORE UPDATE ON preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE consents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    history_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    save_input BOOLEAN NOT NULL DEFAULT FALSE,
    save_result BOOLEAN NOT NULL DEFAULT FALSE,
    consent_type VARCHAR(80) NOT NULL DEFAULT 'analysis_history',
    is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_consents_user_type UNIQUE (user_id, consent_type)
);

CREATE INDEX idx_consents_user_id ON consents(user_id);
CREATE INDEX idx_consents_type ON consents(consent_type);

CREATE TRIGGER update_consents_updated_at
    BEFORE UPDATE ON consents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    overall_emotion VARCHAR(120) NOT NULL,
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    emotion_distribution JSONB NOT NULL DEFAULT '{}'::jsonb,
    summary TEXT NOT NULL,
    context_note TEXT NOT NULL,
    suggested_reply TEXT NOT NULL,
    warning TEXT NOT NULL,
    save_input BOOLEAN NOT NULL DEFAULT FALSE,
    save_result BOOLEAN NOT NULL DEFAULT FALSE,
    consent_type VARCHAR(80) NOT NULL DEFAULT 'analysis_history',
    is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    chat_text TEXT
);

CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_analyzed_at ON analysis_sessions(analyzed_at DESC);
CREATE INDEX idx_analysis_sessions_overall_emotion ON analysis_sessions(overall_emotion);
CREATE INDEX idx_analysis_sessions_emotion_distribution ON analysis_sessions USING GIN (emotion_distribution);

COMMENT ON TABLE users IS 'User accounts for simple bearer-token auth.';
COMMENT ON TABLE profiles IS 'Per-user profile information.';
COMMENT ON TABLE partner_profiles IS 'Per-user partner profile information. Height, weight, and appearance are optional and must not be used to infer emotion.';
COMMENT ON TABLE consents IS 'Per-user privacy and storage consent settings.';
COMMENT ON TABLE analysis_sessions IS 'Per-user emotion analysis history.';
COMMENT ON COLUMN analysis_sessions.chat_text IS 'Original chat text. Must stay NULL unless save_input consent is accepted.';
COMMENT ON COLUMN analysis_sessions.save_input IS 'Whether user explicitly allowed saving original chat text.';
COMMENT ON COLUMN analysis_sessions.save_result IS 'Whether user allowed saving the summarized analysis result.';
