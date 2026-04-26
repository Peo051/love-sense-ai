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

## 4. Ghi chú

- MVP không cần chạy `ai-service`.
- MVP chưa cần database.
- Không commit `.env`, `venv`, `node_modules` hoặc `.next`.
- `POST /api/analyze` đang dùng mock response, chưa gọi LLM thật.
