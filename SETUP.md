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
```

2. Chạy 9Router local trên port 20128

3. Restart backend server

**⚠️ Bảo mật:**
- Không commit file `.env`
- Không hard-code API key
- File `.env` đã được gitignore

Xem chi tiết: [docs/E2E_ANALYZE_LLM_FLOW.md](docs/E2E_ANALYZE_LLM_FLOW.md)

## 5. Ghi chú

- MVP không cần chạy `ai-service`.
- Dữ liệu profile/history/consent đã lưu trong database theo `user_id`.
- Không commit `.env`, `venv`, `node_modules` hoặc `.next`.
- `POST /api/analyze` mặc định dùng mock response, có thể bật LLM thật bằng cách đặt `LLM_MOCK_MODE=false`.
