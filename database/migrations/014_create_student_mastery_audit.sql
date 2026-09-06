-- Migration: Create student_mastery_audit table
-- Created: 2026-09-06
-- Target: PostgreSQL 14+ / Supabase

-- 1. Table: student_mastery_audit
CREATE TABLE IF NOT EXISTS student_mastery_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(code) ON DELETE CASCADE,
    attempt_id UUID NOT NULL REFERENCES student_attempts(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    previous_score DOUBLE PRECISION NOT NULL CHECK (previous_score >= 0.0 AND previous_score <= 1.0),
    new_score DOUBLE PRECISION NOT NULL CHECK (new_score >= 0.0 AND new_score <= 1.0),
    reason TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_mastery_audit_attempt_skill UNIQUE (attempt_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_mastery_audit_user_created ON student_mastery_audit(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_mastery_audit_attempt_id ON student_mastery_audit(attempt_id);
CREATE INDEX IF NOT EXISTS idx_mastery_audit_skill_id ON student_mastery_audit(skill_id);

COMMENT ON TABLE student_mastery_audit IS 'Audit log of all mastery score updates connected to learning attempts';
COMMENT ON COLUMN student_mastery_audit.attempt_id IS 'Student attempt that caused the mastery update';
COMMENT ON COLUMN student_mastery_audit.previous_score IS 'Mastery score before the event';
COMMENT ON COLUMN student_mastery_audit.new_score IS 'Mastery score after the event was applied';
COMMENT ON COLUMN student_mastery_audit.reason IS 'Pedagogical explanation of why the update occurred';
