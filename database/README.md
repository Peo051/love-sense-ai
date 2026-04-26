# Love Emotion Database

Database chưa bắt buộc cho MVP hiện tại. Backend đang dùng in-memory store để phát triển nhanh các module Profile, History và Consent. Khi chuyển sang PostgreSQL/Supabase, chạy các migration theo thứ tự.

## Chạy migrations

```powershell
psql -U postgres -d loveemotion -f migrations/001_create_users.sql
psql -U postgres -d loveemotion -f migrations/002_create_profiles.sql
psql -U postgres -d loveemotion -f migrations/003_create_partner_profiles.sql
psql -U postgres -d loveemotion -f migrations/004_create_preferences.sql
psql -U postgres -d loveemotion -f migrations/005_create_analysis_sessions.sql
psql -U postgres -d loveemotion -f migrations/006_add_consent_and_privacy_controls.sql
```

## Consent fields

Các trường bắt buộc cho cơ chế đồng ý lưu/xóa dữ liệu:

- `save_input`: người dùng có đồng ý lưu nội dung chat gốc không.
- `save_result`: người dùng có đồng ý lưu kết quả phân tích không.
- `consent_type`: loại đồng ý, ví dụ `analysis_history` hoặc `analysis_submission`.
- `is_accepted`: trạng thái đồng ý.
- `accepted_at`: thời điểm người dùng đồng ý.

## Quy tắc lưu chat

- Không lưu `chat_text` mặc định.
- Chỉ lưu `chat_text` khi `save_input = true`, `is_accepted = true` và `accepted_at` có giá trị.
- Nếu chỉ `save_result = true`, chỉ lưu kết quả tổng hợp như cảm xúc, độ tin cậy, tóm tắt, gợi ý và cảnh báo.
- Chiều cao, cân nặng, ngoại hình trong hồ sơ là tùy chọn và không được dùng để suy luận cảm xúc.
