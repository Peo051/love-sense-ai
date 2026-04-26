# Love Emotion Web - Setup MVP

## Yêu cầu

- Python 3.11+ hoặc Python 3.13 như môi trường hiện tại.
- Node.js 20+ và npm.
- PostgreSQL chưa bắt buộc cho MVP.

## 1. Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

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
venv\Scripts\activate
python -m pytest tests\test_analyze.py tests\test_safety_filter.py
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
LLM_PROVIDER=openai
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=your-9router-api-key
LLM_MODEL=gpt-4o-mini
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
- MVP chưa cần database.
- Không commit `.env`, `venv`, `node_modules` hoặc `.next`.
- `POST /api/analyze` mặc định dùng mock response, có thể bật LLM thật bằng cách đặt `LLM_MOCK_MODE=false`.
