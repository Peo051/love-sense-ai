# Love Emotion Database

Database chính là PostgreSQL hoặc Supabase. Backend dùng SQLAlchemy async và driver `asyncpg`.

## Setup Mới

Nếu tạo database mới, chạy schema đầy đủ:

```powershell
psql -U postgres -d loveemotion -f schema.sql
```

Với Supabase, mở SQL Editor và chạy nội dung `schema.sql`, hoặc dùng connection string trong `DATABASE_URL`.

## Chạy Migrations

Nếu muốn chạy theo từng bước:

```powershell
psql -U postgres -d loveemotion -f migrations/001_create_users.sql
psql -U postgres -d loveemotion -f migrations/002_create_profiles.sql
psql -U postgres -d loveemotion -f migrations/003_create_partner_profiles.sql
psql -U postgres -d loveemotion -f migrations/004_create_preferences.sql
psql -U postgres -d loveemotion -f migrations/005_create_analysis_sessions.sql
psql -U postgres -d loveemotion -f migrations/006_add_consent_and_privacy_controls.sql
psql -U postgres -d loveemotion -f migrations/007_add_auth_scoped_models.sql
```

`007_add_auth_scoped_models.sql` đồng bộ schema với SQLAlchemy models hiện tại và thêm các field cần cho auth/user-scoped data.

## Bảng Chính

- `users`: tài khoản auth đơn giản.
- `profiles`: hồ sơ người dùng, một bản ghi cho mỗi user.
- `partner_profiles`: hồ sơ người yêu, một bản ghi cho mỗi user.
- `consents`: cài đặt quyền riêng tư và đồng ý lưu dữ liệu theo user.
- `analysis_sessions`: lịch sử phân tích theo user.

## Consent Fields

- `history_enabled`: user có bật lưu lịch sử không.
- `save_input`: user có đồng ý lưu nội dung chat gốc không.
- `save_result`: user có đồng ý lưu kết quả tổng hợp không.
- `consent_type`: loại đồng ý, ví dụ `privacy_settings` hoặc `analysis_submission`.
- `is_accepted`: trạng thái đồng ý.
- `accepted_at`: thời điểm user đồng ý.

## Quy Tắc Lưu Chat

- Không lưu `chat_text` mặc định.
- Chỉ lưu `chat_text` khi `save_input = true`, `is_accepted = true` và `accepted_at` có giá trị.
- Nếu chỉ `save_result = true`, chỉ lưu kết quả tổng hợp như cảm xúc, độ tin cậy, tóm tắt, gợi ý và cảnh báo.
- Chiều cao, cân nặng, ngoại hình trong hồ sơ là tùy chọn và không được dùng để suy luận cảm xúc.
