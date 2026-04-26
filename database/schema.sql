-- Love Emotion Database Schema
-- PostgreSQL 14+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Drop tables if exists (for clean setup)
DROP TABLE IF EXISTS analysis_sessions CASCADE;
DROP TABLE IF EXISTS preferences CASCADE;
DROP TABLE IF EXISTS partner_profiles CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Profiles table
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 18 AND age <= 100),
    communication_style VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_profiles_user_id ON profiles(user_id);

CREATE TRIGGER update_profiles_updated_at 
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Partner profiles table
CREATE TABLE partner_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    age INTEGER CHECK (age >= 18 AND age <= 100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_partner_profiles_user_id ON partner_profiles(user_id);

CREATE TRIGGER update_partner_profiles_updated_at 
    BEFORE UPDATE ON partner_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Preferences table
CREATE TABLE preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'vi',
    notification_enabled BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_preference UNIQUE (user_id)
);

CREATE INDEX idx_preferences_user_id ON preferences(user_id);

CREATE TRIGGER update_preferences_updated_at 
    BEFORE UPDATE ON preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Analysis sessions table
CREATE TABLE analysis_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chat_text TEXT,
    emotion VARCHAR(50) NOT NULL,
    confidence DECIMAL(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    summary TEXT,
    context_note TEXT,
    suggested_reply TEXT,
    warning TEXT,
    emotion_scores JSONB,
    save_input BOOLEAN NOT NULL DEFAULT FALSE,
    save_result BOOLEAN NOT NULL DEFAULT FALSE,
    consent_type VARCHAR(80) DEFAULT 'analysis_history',
    is_accepted BOOLEAN NOT NULL DEFAULT FALSE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analysis_sessions_user_id ON analysis_sessions(user_id);
CREATE INDEX idx_analysis_sessions_created_at ON analysis_sessions(created_at DESC);
CREATE INDEX idx_analysis_sessions_emotion ON analysis_sessions(emotion);
CREATE INDEX idx_analysis_sessions_emotion_scores ON analysis_sessions USING GIN (emotion_scores);

-- Consent settings table
CREATE TABLE consents (
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

CREATE INDEX idx_consents_user_id ON consents(user_id);
CREATE INDEX idx_consents_type ON consents(consent_type);

CREATE TRIGGER update_consents_updated_at
    BEFORE UPDATE ON consents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE users IS 'User accounts';
COMMENT ON TABLE profiles IS 'User profile information';
COMMENT ON TABLE partner_profiles IS 'Partner profile information';
COMMENT ON TABLE preferences IS 'User preferences and settings';
COMMENT ON TABLE analysis_sessions IS 'History of emotion analysis sessions';
COMMENT ON TABLE consents IS 'User consent settings for saving analysis results and chat content';
COMMENT ON COLUMN analysis_sessions.chat_text IS 'Original chat text. Must stay NULL unless save_input consent is accepted.';
COMMENT ON COLUMN analysis_sessions.save_input IS 'Whether user explicitly allowed saving original chat text.';
COMMENT ON COLUMN analysis_sessions.save_result IS 'Whether user allowed saving analysis result.';
COMMENT ON COLUMN analysis_sessions.consent_type IS 'Consent category used when saving this record.';
COMMENT ON COLUMN analysis_sessions.is_accepted IS 'Whether consent was accepted when this record was saved.';
COMMENT ON COLUMN analysis_sessions.accepted_at IS 'Timestamp when consent was accepted.';
