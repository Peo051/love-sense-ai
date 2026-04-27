# Project Guide

Love Emotion Web là web app phân tích sắc thái cảm xúc trong đoạn hội thoại tình cảm theo hướng hỗ trợ giao tiếp nhẹ nhàng.

## Luồng Chính

1. User có thể đăng ký hoặc đăng nhập bằng email/password.
2. User nhập đoạn chat thủ công và bối cảnh cá nhân hóa.
3. Frontend gửi `POST /api/analyze` đến FastAPI backend.
4. Backend validate dữ liệu, chạy preprocessing đơn giản và mock AI.
5. Backend áp dụng safety filter.
6. Nếu user đăng nhập và có consent hợp lệ, backend lưu lịch sử theo `user_id`.
7. Frontend hiển thị kết quả, phân bố cảm xúc, gợi ý phản hồi và cảnh báo.

## Nguyên Tắc An Toàn

- Không đọc trộm Zalo, Messenger, SMS, thông báo hoặc danh bạ.
- Không kết luận chắc chắn cảm xúc, hành vi hoặc lòng chung thủy của người khác.
- Không đưa lời khuyên thao túng cảm xúc.
- Không lưu nội dung chat mặc định.
- Luôn hiển thị cảnh báo: “Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.”

## Kiến Trúc Backend

- `backend/app/routes/`: route FastAPI.
- `backend/app/schemas/`: Pydantic request/response schemas.
- `backend/app/models/`: SQLAlchemy models.
- `backend/app/services/db_store.py`: repository thao tác profile, history, consent, user data.
- `backend/app/services/llm_client.py`: client gọi provider tương thích OpenAI Chat Completions như 9router.
- `backend/app/services/analysis_policy.py`: cảnh báo an toàn và system prompt dùng chung cho mock/LLM.
- `backend/app/core/auth.py`: dependency lấy user hiện tại từ Bearer token.
- `backend/app/core/security.py`: hash password và tạo JWT.
- `backend/app/database/connection.py`: async engine/session, normalize URL PostgreSQL/Supabase và fallback SQLite dev.
- `database/migrations/`: SQL migrations PostgreSQL/Supabase theo thứ tự.

## Data Ownership

- `profiles.user_id` là unique.
- `partner_profiles.user_id` là unique.
- `consents.user_id + consent_type` là unique.
- `preferences.user_id` là unique.
- `analysis_sessions.user_id` được dùng để lọc lịch sử.
- Mọi endpoint đọc/xóa dữ liệu cá nhân đều dùng `current_user.id`.

## Database

- Dev mặc định có thể dùng `sqlite+aiosqlite:///./love_emotion_dev.db` và tự tạo bảng khi `APP_ENV=development`.
- PostgreSQL/Supabase dùng `DATABASE_URL` trong `backend/.env` và chạy `database/schema.sql` hoặc các migration theo thứ tự.
- Backend test dùng SQLite in-memory riêng qua dependency override, không phụ thuộc database production.

## Quyền Riêng Tư

- `save_input=false` là mặc định.
- `chat_text` nullable trong database.
- Backend chỉ set `chat_text` khi user có token, bật lưu lịch sử và request có `save_input=true`.
- Nếu chỉ `save_result=true`, backend chỉ lưu kết quả tổng hợp.
- Delete endpoints chỉ xóa dữ liệu của user đang đăng nhập.

## Hướng Phát Triển

Ưu tiên tiếp theo là bổ sung migration runner tự động như Alembic, refresh token hoặc session UX tốt hơn, rồi mới tích hợp LLM thật bằng biến môi trường.

## Cấu Hình 9router

Backend đọc các biến:

- `LLM_PROVIDER=9router`
- `LLM_BASE_URL=http://localhost:20128/v1`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_MOCK_MODE=false`

Không ghi API key thật vào source code. `.env.example` chỉ chứa placeholder.
