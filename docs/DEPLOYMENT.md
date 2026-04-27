# Deployment Guide

Tài liệu này chuẩn bị deploy demo cho Love Sense AI / Love Emotion Web. Không commit `.env`, API key, token hoặc secret vào repository.

## Kiến Trúc Đề Xuất

- Frontend: Vercel, source directory `frontend/`.
- Backend: Render hoặc Railway, source directory `backend/`.
- Database: Supabase PostgreSQL.
- LLM: 9Router hoặc provider tương thích OpenAI Chat Completions.

Không hard-code domain production trong code. Frontend, backend, CORS, database và LLM đều phải đọc từ biến môi trường của nền tảng deploy.

## Supabase PostgreSQL

1. Tạo project Supabase mới.
2. Mở SQL Editor và chạy `database/schema.sql`.
3. Nếu muốn chạy theo migration, chạy lần lượt:

```text
database/migrations/001_create_users.sql
database/migrations/002_create_profiles.sql
database/migrations/003_create_partner_profiles.sql
database/migrations/004_create_preferences.sql
database/migrations/005_create_analysis_sessions.sql
database/migrations/006_add_consent_and_privacy_controls.sql
database/migrations/007_add_auth_scoped_models.sql
database/migrations/008_harden_user_scoped_persistence.sql
```

4. Lấy connection string PostgreSQL từ Supabase và đặt vào `DATABASE_URL` trên backend hosting.
5. Không bật SQLite fallback ở production. Khi `APP_ENV=production`, backend sẽ báo lỗi cấu hình rõ ràng nếu `DATABASE_URL` không phải PostgreSQL/Supabase.

## Backend: Render Hoặc Railway

Thiết lập service Python/FastAPI từ thư mục `backend/`.

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Biến môi trường production bắt buộc:

```text
APP_ENV=production
FRONTEND_URL=https://<frontend-app-domain>
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<database>
DATABASE_AUTO_CREATE=false
SECRET_KEY=<strong-random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

CORS:

```text
ALLOWED_ORIGINS=https://<frontend-app-domain>
```

Nếu không set `ALLOWED_ORIGINS`, backend production sẽ chỉ dùng `FRONTEND_URL` thay vì danh sách localhost mặc định.

LLM mock mode an toàn:

```text
LLM_PROVIDER=mock
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=
LLM_MODEL=api_models_all
LLM_MOCK_MODE=true
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
```

LLM thật qua 9Router/OpenAI-compatible provider:

```text
LLM_PROVIDER=9router
LLM_BASE_URL=https://<provider-base-url>/v1
LLM_API_KEY=<set-in-hosting-secret-store>
LLM_MODEL=<model-or-alias>
LLM_MOCK_MODE=false
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
```

Rate limit cho `POST /api/analyze`:

```text
RATE_LIMIT_MAX_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

Các tên cũ `ANALYZE_RATE_LIMIT_REQUESTS` và `ANALYZE_RATE_LIMIT_WINDOW_SECONDS` vẫn được backend đọc để tránh phá môi trường cũ, nhưng production nên dùng `RATE_LIMIT_*`.

## Frontend: Vercel

Thiết lập project Vercel từ thư mục `frontend/`.

Build command:

```bash
npm run build
```

Output framework: Next.js.

Biến môi trường production:

```text
NEXT_PUBLIC_API_URL=https://<backend-app-domain>
```

Không đưa `LLM_API_KEY`, `DATABASE_URL`, token hoặc secret vào frontend. Mọi biến `NEXT_PUBLIC_*` đều có thể bị trình duyệt nhìn thấy.

## Checklist Production Env

Backend:

- `APP_ENV=production`
- `FRONTEND_URL`
- `ALLOWED_ORIGINS` nếu cần nhiều origin
- `DATABASE_URL`
- `DATABASE_AUTO_CREATE=false`
- `SECRET_KEY`
- `ALGORITHM=HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_MOCK_MODE`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_RETRIES`
- `LLM_RETRY_BASE_DELAY_SECONDS`
- `RATE_LIMIT_MAX_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`

Frontend:

- `NEXT_PUBLIC_API_URL`

## Security Và Privacy

- Không commit `.env`, `.env.local`, API key, token hoặc secret.
- Không hard-code domain production trong source code.
- Không đưa `LLM_API_KEY` vào frontend.
- Không lưu `chat_text` mặc định.
- Chỉ lưu `chat_text` khi user bật `save_input=true`.
- Profile, history và consent luôn scoped theo `user_id`.
- User chỉ được đọc/sửa/xóa dữ liệu của chính mình.
- Trang `/privacy` có luồng xóa lịch sử, xóa hồ sơ và xóa toàn bộ dữ liệu user.
- Nếu API key bị lộ, revoke key ở provider ngay, tạo key mới và cập nhật secret trên hosting.

## Pre-Deploy Checks

Backend:

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests
.\venv\Scripts\python.exe -m compileall app
```

Frontend:

```powershell
cd frontend
npm run test
npm run typecheck
npm run build
npm audit
```

Git:

```powershell
git diff --check
git status
```

Kiểm tra staged diff không chứa `.env`, API key, token hoặc secret trước khi commit.

## Manual Smoke Test Sau Deploy

1. Mở frontend deploy URL.
2. Đăng ký/đăng nhập tại `/auth`.
3. Vào `/analyze`, nhập đoạn chat thủ công và phân tích.
4. Tick lưu kết quả, không tick lưu nội dung chat, rồi kiểm tra `/history` không có `chat_text`.
5. Vào `/profile`, lưu hồ sơ và reload để kiểm tra đọc lại.
6. Vào `/privacy`, thử xóa lịch sử/hồ sơ/toàn bộ dữ liệu với xác nhận.
7. Kiểm tra backend `/health` và `/api/health`.
