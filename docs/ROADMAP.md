# Roadmap

## Giai Đoạn 1 - MVP Local

- Frontend `/` và `/analyze`.
- Backend `/health` và `/api/analyze`.
- Mock AI response.
- Cảnh báo an toàn và quyền riêng tư.
- Test frontend cho form `/analyze`.

## Giai Đoạn 2 - Profile, History, Consent

Đã có:

- Hồ sơ cá nhân hóa.
- Hồ sơ người yêu.
- Lịch sử phân tích.
- Checkbox đồng ý lưu kết quả và lưu nội dung chat.
- API xóa một lịch sử, xóa toàn bộ lịch sử, xóa hồ sơ và xóa toàn bộ dữ liệu cá nhân.
- Cài đặt quyền riêng tư.

## Giai Đoạn 3 - Database Và Auth

Đã có:

- PostgreSQL/Supabase schema.
- SQLAlchemy async models.
- SQL migrations.
- Auth email/password bằng Bearer JWT.
- `user_id` cho profile, partner profile, history và consent.
- Kiểm soát để mỗi user chỉ thấy dữ liệu của mình.
- Quy tắc không lưu chat mặc định.
- Cấu hình LLM provider tương thích OpenAI Chat Completions, gồm 9router.

Việc nên làm tiếp:

- Chạy migration trên PostgreSQL/Supabase thật và kiểm tra thủ công full flow.
- Bổ sung UX yêu cầu đăng nhập rõ hơn ở `/profile`, `/history`, `/privacy`.
- Thêm integration test với PostgreSQL test container nếu môi trường cho phép.

## Giai Đoạn 4 - LLM Thật

- Tích hợp LLM API bằng biến môi trường, không hard-code key.
- Prompt safety rõ ràng và output JSON theo schema `AnalyzeResponse`.
- Không log nội dung chat nhạy cảm nếu user không đồng ý lưu.

## Giai Đoạn 5 - Production Readiness

- Refresh token hoặc session strategy tốt hơn.
- Rate limit.
- Error monitoring.
- E2E tests.
- Deployment frontend/backend.
