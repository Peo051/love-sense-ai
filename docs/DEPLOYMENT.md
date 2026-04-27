# Deployment Guide

Tài liệu này chuẩn bị deploy demo cho Love Sense AI / Love Emotion Web.

## Backend Environment

Bắt buộc cấu hình riêng trên hosting, không commit `.env`:

```text
APP_ENV=production
FRONTEND_URL=https://your-frontend-domain
ALLOWED_ORIGINS=https://your-frontend-domain
DATABASE_URL=postgresql://...
DATABASE_AUTO_CREATE=false
SECRET_KEY=<strong-random-secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
LLM_MOCK_MODE=true
```

Nếu bật 9Router/OpenAI-compatible provider:

```text
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=<set-in-hosting-secret-store>
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
```

Rate limit:

```text
ANALYZE_RATE_LIMIT_REQUESTS=20
ANALYZE_RATE_LIMIT_WINDOW_SECONDS=60
```

## Database

Production nên dùng PostgreSQL hoặc Supabase.

1. Tạo database.
2. Chạy `database/schema.sql`, hoặc chạy migrations theo thứ tự từ `001` đến `008`.
3. Đặt `DATABASE_AUTO_CREATE=false`.
4. Không dùng SQLite fallback cho production.

## Frontend Environment

```text
NEXT_PUBLIC_API_URL=https://your-backend-domain
```

Không đưa secret vào frontend env. Biến `NEXT_PUBLIC_*` sẽ được expose ra trình duyệt.

## Pre-Deploy Checks

Backend:

```powershell
cd backend
.\venv\Scripts\python.exe -m pytest tests
```

Frontend:

```powershell
cd frontend
npm run test
npm run typecheck
npm run build
npm audit
```

## Privacy Checklist

- Không lưu `chat_text` mặc định.
- Chỉ lưu `chat_text` khi `save_input=true`.
- Profile/history/consent scoped theo `user_id`.
- `/api/analyze` có rate limit.
- LLM lỗi thì fallback response an toàn.
- Không log API key, token hoặc nội dung chat.
