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

Chỉnh `DATABASE_URL` trong `.env`:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/loveemotion
SECRET_KEY=change-this-for-local-dev
```

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
LLM_API_KEY=your_9router_api_key_here
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
```

Không commit `.env` hoặc API key thật. Nếu provider lỗi hoặc thiếu cấu hình, `/api/analyze` trả `502` thay vì âm thầm fallback sang mock.

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
python -m pytest tests
```
