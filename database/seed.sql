-- Seed data for Love Emotion database
-- This file contains sample data for development and testing

-- Insert sample users
INSERT INTO users (id, email, hashed_password, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE),
    ('550e8400-e29b-41d4-a716-446655440002', 'user2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE),
    ('550e8400-e29b-41d4-a716-446655440003', 'user3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE)
ON CONFLICT (email) DO NOTHING;

-- Insert sample profiles
INSERT INTO profiles (user_id, name, age, communication_style) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Nguyễn Văn A', 25, 'direct'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Trần Thị B', 23, 'emotional'),
    ('550e8400-e29b-41d4-a716-446655440003', 'Lê Văn C', 27, 'indirect')
ON CONFLICT DO NOTHING;

-- Insert sample partner profiles
INSERT INTO partner_profiles (user_id, name, age, notes) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Trần Thị D', 24, 'Thích giao tiếp trực tiếp'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Nguyễn Văn E', 26, 'Hay quan tâm và chu đáo')
ON CONFLICT DO NOTHING;

-- Insert sample preferences
INSERT INTO preferences (user_id, language, notification_enabled, theme) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'vi', TRUE, 'light'),
    ('550e8400-e29b-41d4-a716-446655440002', 'vi', TRUE, 'dark'),
    ('550e8400-e29b-41d4-a716-446655440003', 'en', FALSE, 'light')
ON CONFLICT (user_id) DO NOTHING;

-- Insert sample analysis sessions
INSERT INTO analysis_sessions (user_id, message, emotion, confidence, suggested_reply, emotion_scores) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'Em yêu anh!',
        'Yêu thương',
        0.85,
        'Anh cũng yêu em!',
        '[{"name": "Yêu thương", "value": 0.85}, {"name": "Hạnh phúc", "value": 0.70}]'::jsonb
    ),
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'Em nhớ anh quá!',
        'Hạnh phúc',
        0.80,
        'Anh cũng nhớ em lắm!',
        '[{"name": "Hạnh phúc", "value": 0.80}, {"name": "Yêu thương", "value": 0.75}]'::jsonb
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'Hôm nay em buồn quá',
        'Buồn',
        0.75,
        'Anh ở đây với em!',
        '[{"name": "Buồn", "value": 0.75}, {"name": "Lo lắng", "value": 0.60}]'::jsonb
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'Anh có khỏe không?',
        'Quan tâm',
        0.70,
        'Anh khỏe, cảm ơn em!',
        '[{"name": "Quan tâm", "value": 0.70}, {"name": "Yêu thương", "value": 0.65}]'::jsonb
    );

-- Display summary
SELECT 'Seed data inserted successfully!' as message;
SELECT 'Users: ' || COUNT(*) as count FROM users;
SELECT 'Profiles: ' || COUNT(*) as count FROM profiles;
SELECT 'Partner Profiles: ' || COUNT(*) as count FROM partner_profiles;
SELECT 'Preferences: ' || COUNT(*) as count FROM preferences;
SELECT 'Analysis Sessions: ' || COUNT(*) as count FROM analysis_sessions;
