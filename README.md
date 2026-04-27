# Love Emotion Web

Love Emotion Web là web app hỗ trợ phân tích sắc thái cảm xúc trong đoạn hội thoại tình cảm. Ứng dụng chỉ phân tích nội dung người dùng nhập thủ công, không đọc trộm tin nhắn, không kết luận chắc chắn cảm xúc của người khác và không lưu nội dung chat mặc định.

## Hiện Có

- Frontend Next.js: `/`, `/analyze`, `/auth`, `/profile`, `/history`, `/privacy`.
- Backend FastAPI: `/health`, `/api/analyze`, `/api/register`, `/api/token`, `/api/me`, `/api/profile`, `/api/history`, `/api/consent`, `/api/user-data`.
- PostgreSQL/Supabase schema và SQL migrations trong `database/`.
- SQLAlchemy async models cho user, profile, partner profile, consent và analysis history.
- Auth đơn giản bằng email/password và Bearer JWT.
- Tích hợp LLM provider tương thích OpenAI Chat Completions, gồm 9router local qua `LLM_*`.
- Dữ liệu profile/history/consent luôn được lọc theo `user_id`.
- Consent rõ ràng: lưu kết quả và lưu nội dung chat là hai lựa chọn riêng.
- Test frontend cho form `/analyze` và test backend cho auth, analyze, profile, history, consent.

## Cấu Trúc

```text
love-emotion-web/
├── frontend/      # Next.js + TypeScript + Tailwind CSS
├── backend/       # FastAPI + Pydantic + SQLAlchemy async
├── ai-service/    # Thử nghiệm AI service, chưa cần cho MVP
├── database/      # PostgreSQL/Supabase schema và migrations
├── docs/          # Tài liệu dự án
└── README.md
```

## Chạy Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Nếu chưa có PostgreSQL/Supabase ở máy dev, giữ mặc định `DATABASE_URL=sqlite+aiosqlite:///./love_emotion_dev.db`; backend sẽ tự tạo bảng khi `APP_ENV=development`. Khi dùng PostgreSQL hoặc Supabase, cấu hình `DATABASE_URL` trong `backend/.env` và chạy schema/migrations trong `database/`. App tự chuyển `postgresql://` hoặc `postgres://` thành driver async `postgresql+asyncpg://`.

Để bật 9router local, đặt trong `backend/.env`:

```text
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=your_9router_api_key_here
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
```

Kiểm tra: `http://localhost:8000/health`

## Chạy Frontend

```powershell
cd frontend
npm install
npm run dev
```

Mở: `http://localhost:3000/analyze`

## Database

Setup database mới:

```powershell
cd database
psql -U postgres -d loveemotion -f schema.sql
```

Hoặc chạy migration theo thứ tự:

```powershell
psql -U postgres -d loveemotion -f migrations/001_create_users.sql
psql -U postgres -d loveemotion -f migrations/002_create_profiles.sql
psql -U postgres -d loveemotion -f migrations/003_create_partner_profiles.sql
psql -U postgres -d loveemotion -f migrations/004_create_preferences.sql
psql -U postgres -d loveemotion -f migrations/005_create_analysis_sessions.sql
psql -U postgres -d loveemotion -f migrations/006_add_consent_and_privacy_controls.sql
psql -U postgres -d loveemotion -f migrations/007_add_auth_scoped_models.sql
psql -U postgres -d loveemotion -f migrations/008_harden_user_scoped_persistence.sql
```

## Test

Backend:

```powershell
cd backend
venv\Scripts\activate
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

## Quy Tắc Riêng Tư

- Không lưu `chat_text` mặc định.
- `save_result=true` chỉ lưu kết quả tổng hợp nếu user đã bật lưu lịch sử.
- `save_input=true` mới cho phép lưu `chat_text`.
- Profile, history và consent luôn thuộc về user đang đăng nhập.
- Endpoint xóa dữ liệu chỉ xóa dữ liệu của user hiện tại.

## Tài Liệu

- [Testing Guide](docs/TESTING.md)
- [Project Guide](docs/PROJECT_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Roadmap](docs/ROADMAP.md)
