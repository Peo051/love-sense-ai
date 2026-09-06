-- Migration: Create student_skill_mastery table
-- Created: 2026-09-06
-- Target: PostgreSQL 14+ / Supabase

-- 1. Table: student_skill_mastery
CREATE TABLE IF NOT EXISTS student_skill_mastery (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id VARCHAR(50) NOT NULL REFERENCES skills(code) ON DELETE CASCADE,
    mastery_score DOUBLE PRECISION NOT NULL DEFAULT 0.5 CHECK (mastery_score >= 0.0 AND mastery_score <= 1.0),
    success_count INT NOT NULL DEFAULT 0 CHECK (success_count >= 0),
    failure_count INT NOT NULL DEFAULT 0 CHECK (failure_count >= 0),
    hint_count INT NOT NULL DEFAULT 0 CHECK (hint_count >= 0),
    last_practiced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_skill_mastery_user_skill UNIQUE (user_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_student_skill_mastery_user_id ON student_skill_mastery(user_id);
CREATE INDEX IF NOT EXISTS idx_student_skill_mastery_skill_id ON student_skill_mastery(skill_id);
CREATE INDEX IF NOT EXISTS idx_student_skill_mastery_user_score ON student_skill_mastery(user_id, mastery_score);

CREATE TRIGGER update_student_skill_mastery_updated_at
    BEFORE UPDATE ON student_skill_mastery
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE student_skill_mastery IS 'Tracks individual student mastery progression across canonical C# OOP skills';
COMMENT ON COLUMN student_skill_mastery.mastery_score IS 'Estimated competence score bounded in [0.0, 1.0], initialized to neutral 0.5';
COMMENT ON COLUMN student_skill_mastery.success_count IS 'Total successful practice attempts on this skill';
COMMENT ON COLUMN student_skill_mastery.failure_count IS 'Total unresolved/failed practice attempts on this skill';
COMMENT ON COLUMN student_skill_mastery.hint_count IS 'Total hint requests used during practice on this skill';
COMMENT ON COLUMN student_skill_mastery.last_practiced_at IS 'Timestamp of most recent practice activity on this skill';
