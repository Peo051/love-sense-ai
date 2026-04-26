-- Migration: Create preferences table
-- Created: 2026-04-26

CREATE TABLE IF NOT EXISTS preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) DEFAULT 'vi',
    notification_enabled BOOLEAN DEFAULT TRUE,
    theme VARCHAR(20) DEFAULT 'light',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_user_preference UNIQUE (user_id)
);

-- Create index on user_id
CREATE INDEX idx_preferences_user_id ON preferences(user_id);

-- Add trigger to update updated_at
CREATE TRIGGER update_preferences_updated_at 
    BEFORE UPDATE ON preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment
COMMENT ON TABLE preferences IS 'User preferences and settings';
COMMENT ON COLUMN preferences.language IS 'Preferred language: vi, en';
COMMENT ON COLUMN preferences.theme IS 'UI theme: light, dark';
