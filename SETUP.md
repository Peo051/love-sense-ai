# Love Emotion Web - Setup MVP

## Yêu cầu

- Python 3.11+ hoặc Python 3.13 như môi trường hiện tại.
- Node.js 20+ và npm.
- PostgreSQL/Supabase khuyến nghị cho dữ liệu thật; dev có SQLite fallback.

## 1. Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Mặc định backend dùng `sqlite+aiosqlite:///./love_emotion_dev.db` và tự tạo bảng khi `APP_ENV=development`. Nếu dùng PostgreSQL/Supabase, đổi `DATABASE_URL` trong `backend/.env` và chạy `database/schema.sql` hoặc các migration.

Kiểm tra:

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

## 2. Frontend

Mở terminal khác:

```powershell
cd frontend
npm install
npm run dev
```

Mở `http://localhost:3000/analyze`.

### Firebase Google Login

Để dùng Google Login local:

1. Tạo Firebase project.
2. Bật Authentication -> Google provider.
3. Thêm `localhost` vào Authorized domains.
4. Điền Firebase Web SDK config vào `frontend/.env.local`:

```env
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
```

5. Điền Firebase Admin credential JSON vào `backend/.env`:

```env
FIREBASE_SERVICE_ACCOUNT_JSON=
```

Không commit hai file env này. Nếu chưa cấu hình Firebase, `/api/analyze` vẫn dùng được ở chế độ demo không đăng nhập, nhưng `/profile`, `/history`, `/privacy` sẽ yêu cầu đăng nhập.

## 3. Test

Backend:

```powershell
cd backend
venv\Scripts\python.exe -m pytest tests
```

Frontend:

```powershell
cd frontend
npm run test
npm run typecheck
npm run build
npm audit
```

## 4. LLM Configuration (Optional)

Backend mặc định chạy ở **Mock Mode** (`LLM_MOCK_MODE=true`) để test tự động và development.

### Chạy với LLM thật (9Router)

1. Cấu hình `backend/.env`:

```env
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=2
LLM_RETRY_BASE_DELAY_SECONDS=0.25
RATE_LIMIT_MAX_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
```

2. Chạy 9Router local trên port 20128

3. Restart backend server

`LLM_MAX_RETRIES=2` nghĩa là backend thử lại tối đa 2 lần sau lần gọi đầu tiên cho lỗi tạm thời như timeout, `429`, hoặc `5xx`. Không retry lỗi schema, validation hoặc input. Nếu provider vẫn lỗi, backend fallback mock response an toàn để UI vẫn hiển thị đúng format. Rate limit production nên dùng `RATE_LIMIT_MAX_REQUESTS` và `RATE_LIMIT_WINDOW_SECONDS`; backend vẫn đọc alias cũ `ANALYZE_RATE_LIMIT_*` để không phá môi trường dev cũ.

**⚠️ Bảo mật:**
- Không commit file `.env`
- Không hard-code API key
- File `.env` đã được gitignore

Xem chi tiết: [docs/E2E_ANALYZE_LLM_FLOW.md](docs/E2E_ANALYZE_LLM_FLOW.md)

## 5. Deploy

Xem checklist deploy frontend/backend/database tại [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). Khi `APP_ENV=production`, backend yêu cầu `FRONTEND_URL`, `DATABASE_URL` PostgreSQL/Supabase và `SECRET_KEY` thật; SQLite fallback chỉ dành cho development.

Xem thêm:
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Firebase Auth Guide](docs/AUTH_FIREBASE.md)
- [Privacy Design](docs/PRIVACY_DESIGN.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## 6. Ghi chú

- MVP không cần chạy `ai-service`.
- Dữ liệu profile/history/consent đã lưu trong database theo `user_id`.
- Không commit `.env`, `venv`, `node_modules` hoặc `.next`.
- `POST /api/analyze` mặc định dùng mock response, có thể bật LLM thật bằng cách đặt `LLM_MOCK_MODE=false`.
