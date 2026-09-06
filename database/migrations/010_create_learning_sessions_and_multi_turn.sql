-- Migration: Create learning_sessions, student_attempts, tutor_messages
-- Created: 2026-09-06
-- Target: PostgreSQL 14+ / Supabase

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Table: learning_sessions
CREATE TABLE IF NOT EXISTS learning_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(50) NOT NULL DEFAULT 'csharp',
    topic VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_learning_sessions_user_id ON learning_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_created_at ON learning_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_learning_sessions_updated_at ON learning_sessions(updated_at DESC);

CREATE TRIGGER update_learning_sessions_updated_at
    BEFORE UPDATE ON learning_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 2. Table: student_attempts
CREATE TABLE IF NOT EXISTS student_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    problem_reference TEXT NOT NULL,
    diagnosis JSONB,
    hint_progression JSONB,
    success_state VARCHAR(50) NOT NULL DEFAULT 'in_progress',
    save_input BOOLEAN NOT NULL DEFAULT FALSE,
    student_code TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_student_attempts_code_requires_consent CHECK (student_code IS NULL OR save_input IS TRUE)
);

CREATE INDEX IF NOT EXISTS idx_student_attempts_session_id ON student_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_student_attempts_created_at ON student_attempts(created_at ASC);

-- 3. Table: tutor_messages
CREATE TABLE IF NOT EXISTS tutor_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES learning_sessions(id) ON DELETE CASCADE,
    attempt_id UUID REFERENCES student_attempts(id) ON DELETE SET NULL,
    role VARCHAR(30) NOT NULL,
    sanitized_textual_message TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tutor_messages_session_id ON tutor_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_attempt_id ON tutor_messages(attempt_id);
CREATE INDEX IF NOT EXISTS idx_tutor_messages_created_at ON tutor_messages(created_at ASC);

COMMENT ON TABLE learning_sessions IS 'Multi-turn learning sessions for adaptive programming tutoring';
COMMENT ON TABLE student_attempts IS 'Student problem attempts with consent-aware code storage';
COMMENT ON TABLE tutor_messages IS 'Conversational multi-turn tutor and student messages';
COMMENT ON COLUMN student_attempts.student_code IS 'Untrusted student code. Must remain NULL unless save_input is TRUE';
