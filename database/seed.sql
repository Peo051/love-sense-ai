-- Seed data for Love Emotion database
-- Dữ liệu mẫu chỉ dùng cho development/demo.

INSERT INTO users (id, email, hashed_password, is_active) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'user1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE),
    ('550e8400-e29b-41d4-a716-446655440002', 'user2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE),
    ('550e8400-e29b-41d4-a716-446655440003', 'user3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU2u3ZW', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO profiles (user_id, nickname, primary_language, communication_style, relationship_status) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'Nguyễn Văn A', 'Tiếng Việt', 'Trực tiếp nhưng nhẹ nhàng', 'Đang yêu'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Trần Thị B', 'Tiếng Việt', 'Cảm xúc, cần được lắng nghe', 'Đang tìm hiểu'),
    ('550e8400-e29b-41d4-a716-446655440003', 'Lê Văn C', 'Tiếng Việt', 'Ít nói, thích rõ ràng', 'Đang yêu')
ON CONFLICT (user_id) DO UPDATE SET
    nickname = EXCLUDED.nickname,
    primary_language = EXCLUDED.primary_language,
    communication_style = EXCLUDED.communication_style,
    relationship_status = EXCLUDED.relationship_status;

INSERT INTO partner_profiles (
    user_id,
    nickname,
    likes,
    dislikes,
    texting_style,
    when_happy,
    when_sad,
    when_angry,
    likes_checkins,
    dislikes_repeated_questions,
    appearance,
    private_notes
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'Bạn D',
        'Nhạc acoustic, đi dạo',
        'Bị hỏi dồn',
        'Trả lời ngắn khi mệt',
        'Nhắn nhiều hơn và dùng giọng vui',
        'Ít nói, cần được lắng nghe',
        'Cần không gian riêng',
        TRUE,
        TRUE,
        '',
        'Không dùng ngoại hình để suy luận cảm xúc.'
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'Bạn E',
        'Tin nhắn quan tâm ngắn gọn',
        'Bị ép trả lời ngay',
        'Thường phản hồi chậm khi bận',
        'Chủ động hỏi han',
        'Im lặng một lúc',
        'Tránh tranh luận dài',
        TRUE,
        TRUE,
        '',
        ''
    )
ON CONFLICT (user_id) DO UPDATE SET
    nickname = EXCLUDED.nickname,
    likes = EXCLUDED.likes,
    dislikes = EXCLUDED.dislikes,
    texting_style = EXCLUDED.texting_style,
    when_happy = EXCLUDED.when_happy,
    when_sad = EXCLUDED.when_sad,
    when_angry = EXCLUDED.when_angry,
    likes_checkins = EXCLUDED.likes_checkins,
    dislikes_repeated_questions = EXCLUDED.dislikes_repeated_questions,
    appearance = EXCLUDED.appearance,
    private_notes = EXCLUDED.private_notes;

INSERT INTO preferences (user_id, language, notification_enabled, theme) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'vi', TRUE, 'light'),
    ('550e8400-e29b-41d4-a716-446655440002', 'vi', TRUE, 'light'),
    ('550e8400-e29b-41d4-a716-446655440003', 'vi', FALSE, 'light')
ON CONFLICT (user_id) DO UPDATE SET
    language = EXCLUDED.language,
    notification_enabled = EXCLUDED.notification_enabled,
    theme = EXCLUDED.theme;

INSERT INTO consents (
    user_id,
    history_enabled,
    save_input,
    save_result,
    consent_type,
    is_accepted,
    accepted_at
) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', TRUE, FALSE, TRUE, 'privacy_settings', TRUE, CURRENT_TIMESTAMP),
    ('550e8400-e29b-41d4-a716-446655440002', TRUE, TRUE, TRUE, 'privacy_settings', TRUE, CURRENT_TIMESTAMP)
ON CONFLICT (user_id, consent_type) DO UPDATE SET
    history_enabled = EXCLUDED.history_enabled,
    save_input = EXCLUDED.save_input,
    save_result = EXCLUDED.save_result,
    is_accepted = EXCLUDED.is_accepted,
    accepted_at = EXCLUDED.accepted_at;

INSERT INTO analysis_sessions (
    user_id,
    overall_emotion,
    confidence,
    emotion_distribution,
    summary,
    context_note,
    suggested_reply,
    warning,
    save_input,
    save_result,
    consent_type,
    is_accepted,
    accepted_at,
    chat_text
) VALUES
    (
        '550e8400-e29b-41d4-a716-446655440001',
        'mệt mỏi / né tránh nhẹ',
        0.72,
        '{"mệt_mỏi": 0.35, "né_tránh": 0.25, "buồn": 0.20, "trung_lập": 0.20}'::jsonb,
        'Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều.',
        'Nên phản hồi nhẹ nhàng thay vì hỏi dồn.',
        'Em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.',
        'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.',
        FALSE,
        TRUE,
        'analysis_submission',
        TRUE,
        CURRENT_TIMESTAMP,
        NULL
    ),
    (
        '550e8400-e29b-41d4-a716-446655440002',
        'quan tâm / hơi lo lắng',
        0.68,
        '{"quan_tâm": 0.40, "lo_lắng": 0.28, "trung_lập": 0.32}'::jsonb,
        'Đoạn chat có thể cho thấy nhu cầu được quan tâm và phản hồi rõ ràng hơn.',
        'Người này thích được hỏi thăm nhưng không thích bị ép trả lời ngay.',
        'Anh hiểu rồi, em cứ từ từ nha. Khi nào em tiện mình nói thêm cũng được.',
        'Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.',
        TRUE,
        TRUE,
        'analysis_submission',
        TRUE,
        CURRENT_TIMESTAMP,
        'A: Em sao vậy?\nB: Em hơi mệt thôi.'
    );

SELECT 'Seed data inserted successfully!' AS message;
SELECT 'Users: ' || COUNT(*) AS count FROM users;
SELECT 'Profiles: ' || COUNT(*) AS count FROM profiles;
SELECT 'Partner Profiles: ' || COUNT(*) AS count FROM partner_profiles;
SELECT 'Preferences: ' || COUNT(*) AS count FROM preferences;
SELECT 'Consents: ' || COUNT(*) AS count FROM consents;
SELECT 'Analysis Sessions: ' || COUNT(*) AS count FROM analysis_sessions;
