-- Migration: Replace relationship profile with student profile
-- Created: 2026-09-06
-- Target: PostgreSQL 14+ / Supabase

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Table: student_profiles
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    programming_language VARCHAR(50) NOT NULL DEFAULT 'csharp',
    skill_level VARCHAR(50) NOT NULL DEFAULT 'beginner',
    current_course VARCHAR(120),
    preferred_explanation VARCHAR(50) NOT NULL DEFAULT 'step_by_step',
    solution_preference VARCHAR(50) NOT NULL DEFAULT 'hint_first',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_student_profiles_language CHECK (programming_language = 'csharp'),
    CONSTRAINT ck_student_profiles_skill_level CHECK (skill_level = 'beginner'),
    CONSTRAINT ck_student_profiles_preferred_explanation CHECK (preferred_explanation IN ('concise', 'step_by_step', 'example_first')),
    CONSTRAINT ck_student_profiles_solution_preference CHECK (solution_preference IN ('hint_first', 'balanced'))
);

CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);

CREATE TRIGGER update_student_profiles_updated_at
    BEFORE UPDATE ON student_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE student_profiles IS 'Student learning profile for adaptive C# OOP programming tutor';
COMMENT ON COLUMN student_profiles.preferred_explanation IS 'Preferred pedagogical explanation style: concise, step_by_step, example_first';
COMMENT ON COLUMN student_profiles.solution_preference IS 'Pedagogical solution exposure preference: hint_first, balanced';

-- 2. Clean isolation from historical relationship schema
-- Notice: We deliberately DO NOT copy, reinterpret, or map old romantic profile columns into student data.
DROP TABLE IF EXISTS partner_profiles CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;
