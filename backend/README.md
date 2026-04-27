# Love Emotion Backend

Backend FastAPI cho Love Emotion Web.

## Công Nghệ

- FastAPI
- Pydantic
- SQLAlchemy async
- PostgreSQL/Supabase qua `asyncpg`
- Bearer JWT auth
- Pytest

## Cài Đặt

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Mặc định `.env.example` dùng SQLite file để dev không cần chuẩn bị database trước:

```text
DATABASE_URL=sqlite+aiosqlite:///./love_emotion_dev.db
DATABASE_AUTO_CREATE=true
SECRET_KEY=change-this-for-local-dev
```

Khi dùng PostgreSQL hoặc Supabase, đổi `DATABASE_URL` và chạy schema/migrations trong `database/`:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/loveemotion
DATABASE_AUTO_CREATE=false
SECRET_KEY=change-this-for-local-dev
```

Backend tự chuyển `postgresql://` hoặc `postgres://` thành driver async `postgresql+asyncpg://`.

## Chạy Server

```powershell
uvicorn app.main:app --reload --port 8000
```

API chạy tại `http://localhost:8000`.

## Endpoint Chính

- `GET /health`
- `GET /api/health`
- `POST /api/register`
- `POST /api/token`
- `GET /api/me`
- `POST /api/analyze`
- `GET|POST|DELETE /api/profile`
- `GET /api/history`
- `GET|DELETE /api/history/{id}`
- `DELETE /api/history`
- `GET|POST /api/consent`
- `DELETE /api/user-data`

Swagger UI: `http://localhost:8000/docs`

## LLM / 9router

Mặc định backend dùng mock để test ổn định. Để gọi 9router hoặc provider tương thích OpenAI Chat Completions, cấu hình trong `.env`:

```text
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
ANALYZE_RATE_LIMIT_REQUESTS=20
ANALYZE_RATE_LIMIT_WINDOW_SECONDS=60
```

Không commit `.env` hoặc API key thật. Khi mock mode tắt, backend gọi provider với timeout, retry có kiểm soát cho lỗi tạm thời, rồi fallback mock response an toàn nếu provider vẫn lỗi. Lỗi cấu hình LLM không được log kèm API key.

## Rate Limit

`POST /api/analyze` có in-memory rate limit cho MVP:

- Scope theo `user_id` nếu request có Bearer token hợp lệ.
- Nếu chưa đăng nhập hoặc token không hợp lệ, scope theo IP client.
- Mặc định: `ANALYZE_RATE_LIMIT_REQUESTS=20` trong `ANALYZE_RATE_LIMIT_WINDOW_SECONDS=60`.
- Vượt giới hạn trả `429` và header `Retry-After`.

## Auth Và Phân Quyền Dữ Liệu

- User đăng ký bằng email/password tại `POST /api/register`.
- User đăng nhập bằng OAuth2 password form tại `POST /api/token`.
- Frontend gửi `Authorization: Bearer <token>` cho profile, history, consent và delete data.
- Backend luôn lọc profile/history/consent theo `current_user.id`.
- `POST /api/analyze` vẫn cho phép phân tích khi chưa đăng nhập, nhưng chỉ lưu lịch sử khi có user đăng nhập và có consent hợp lệ.

## Quy Tắc Lưu Dữ Liệu

- Không lưu nội dung chat mặc định.
- `save_result=true` chỉ lưu kết quả tổng hợp.
- `save_input=true` mới lưu `chat_text`.
- `history_enabled=false` trong consent sẽ chặn lưu lịch sử.
- `chat_text` bị để `NULL` nếu user chưa đồng ý lưu nội dung chat.

## Test

```powershell
venv\Scripts\python.exe -m pytest tests
```
