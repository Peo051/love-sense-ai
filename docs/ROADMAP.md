# Roadmap

## Giai đoạn 1 - MVP local

- Frontend `/` và `/analyze`.
- Backend `/health` và `/api/analyze`.
- Mock AI response.
- Cảnh báo an toàn và quyền riêng tư.

## Giai đoạn 2 - Profile, History, Consent

Đã có module in-memory để phát triển sau MVP:

- Hồ sơ cá nhân hóa.
- Hồ sơ người yêu.
- Lịch sử phân tích.
- Checkbox đồng ý lưu kết quả và lưu nội dung chat.
- API xóa một lịch sử, xóa toàn bộ lịch sử, xóa hồ sơ và xóa toàn bộ dữ liệu.

Việc còn lại trước production:

- Thay in-memory store bằng PostgreSQL/Supabase.
- Gắn dữ liệu theo user thật sau khi có authentication.
- Thêm migration đầy đủ cho profile fields mới nếu dùng database.

## Giai đoạn 3 - LLM thật

- Tích hợp LLM API bằng biến môi trường, không hard-code key.
- Prompt safety rõ ràng.
- Không log nội dung chat nhạy cảm nếu người dùng không đồng ý lưu.

## Giai đoạn 4 - Production readiness

- Authentication.
- Rate limit.
- Error monitoring.
- E2E tests.
- Deployment frontend/backend.
