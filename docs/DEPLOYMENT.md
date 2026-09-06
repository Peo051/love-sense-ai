# Deployment Guide

Tài liệu này chuẩn bị deploy demo cho Love Sense AI / Love Emotion Web. Không commit `.env`, API key, token hoặc secret vào repository.

Live demo hiện tại: https://love-sense-ai.vercel.app

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
database/migrations/009_add_firebase_uid_to_users.sql
```

4. Sau khi merge Firebase Auth, bắt buộc chạy migration `009_add_firebase_uid_to_users.sql` trên production database. Nếu bỏ qua bước này, request có Firebase token có thể lỗi `column users.firebase_uid does not exist`.
5. Có thể kiểm tra nhanh cột đã tồn tại bằng SQL:

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'users'
  AND column_name = 'firebase_uid';
```

6. Lấy connection string PostgreSQL từ Supabase và đặt vào `DATABASE_URL` trên backend hosting.
7. Không bật SQLite fallback ở production. Khi `APP_ENV=production`, backend sẽ báo lỗi cấu hình rõ ràng nếu `DATABASE_URL` không phải PostgreSQL/Supabase.

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
FIREBASE_SERVICE_ACCOUNT_JSON=<set-in-hosting-secret-store>
```

CORS:

```text
ALLOWED_ORIGINS=https://<frontend-app-domain>
```

Nếu không set `ALLOWED_ORIGINS`, backend production sẽ chỉ dùng `FRONTEND_URL` thay vì danh sách localhost mặc định.

LLM mock mode an toàn:

```text
LLM_PROVIDER=openai
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=
LLM_MODEL=openai/gpt-4o-mini
LLM_MOCK_MODE=true
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
VISION_MODEL=openai/gpt-4o-mini
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
VISION_MODEL=<optional-vision-model-or-empty>
```

`VISION_MODEL` là tùy chọn. Nếu để trống, backend dùng `LLM_MODEL` cho `/api/ocr/vision`. Backend vẫn đọc alias cũ `VISION_OCR_MODEL` để tương thích môi trường cũ. Không đưa ảnh hoặc base64 vào log; endpoint AI Vision chỉ chạy khi frontend gửi consent riêng của user.

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
NEXT_PUBLIC_API_BASE_URL=https://<backend-app-domain>
NEXT_PUBLIC_FIREBASE_API_KEY=<Firebase web client value>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<project>.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=<project-id>
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=<project>.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<sender-id>
NEXT_PUBLIC_FIREBASE_APP_ID=<app-id>
```

Không đưa `LLM_API_KEY`, `DATABASE_URL`, token hoặc secret vào frontend. Mọi biến `NEXT_PUBLIC_*` đều có thể bị trình duyệt nhìn thấy.

## Firebase Authentication

1. Firebase Console -> Authentication -> Sign-in method -> enable Google provider.
2. Authentication -> Settings -> Authorized domains:
   - `localhost`
   - production frontend domain
3. Vercel nhận Firebase Web SDK config qua `NEXT_PUBLIC_FIREBASE_*`.
4. Render nhận Firebase Admin credential JSON qua `FIREBASE_SERVICE_ACCOUNT_JSON`.
5. Backend map Firebase uid vào `users.firebase_uid`, sau đó dùng `users.id` nội bộ để scope profile/history/consent.

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
- `FIREBASE_SERVICE_ACCOUNT_JSON`
- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_MOCK_MODE`
- `LLM_TIMEOUT_SECONDS`
- `LLM_MAX_RETRIES`
- `LLM_RETRY_BASE_DELAY_SECONDS`
- `VISION_MODEL` nếu provider dùng model vision riêng
- `RATE_LIMIT_MAX_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`

Frontend:

- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_FIREBASE_API_KEY`
- `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`
- `NEXT_PUBLIC_FIREBASE_PROJECT_ID`
- `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`
- `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`
- `NEXT_PUBLIC_FIREBASE_APP_ID`

## Security Và Privacy

- Không commit `.env`, `.env.local`, API key, token hoặc secret.
- Không hard-code domain production trong source code.
- Không đưa `LLM_API_KEY` vào frontend.
- Không đưa Firebase Admin credential vào frontend.
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
2. Đăng nhập Google tại `/login`.
3. Vào `/analyze`, nhập đoạn chat thủ công và phân tích.
4. Thử upload ảnh chat: OCR local phải tạo bản nháp review; AI Vision chỉ gửi ảnh khi user tick consent riêng.
5. Tick lưu kết quả, không tick lưu nội dung chat, rồi kiểm tra `/history` không có `chat_text`.
6. Vào `/profile`, lưu hồ sơ và reload để kiểm tra đọc lại.
7. Vào `/privacy`, thử xóa lịch sử/hồ sơ/toàn bộ dữ liệu với xác nhận.
8. Kiểm tra backend `/health` và `/api/health`.

## Related Docs

- [Setup Guide](../SETUP.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Firebase Auth Guide](AUTH_FIREBASE.md)
- [Privacy Design](PRIVACY_DESIGN.md)
- [Testing Guide](TESTING.md)
