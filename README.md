# Love Sense AI

Love Sense AI là web app hỗ trợ phân tích sắc thái hội thoại tình cảm theo hướng privacy-first. Người dùng chủ động nhập đoạn chat hoặc tải ảnh chụp hội thoại để OCR, kiểm tra lại nội dung, rồi nhận phân tích tham khảo và gợi ý phản hồi nhẹ nhàng.

Ứng dụng không tự truy cập tin nhắn, không kết luận chắc chắn cảm xúc của người khác, không đưa ra lời khuyên thao túng và không lưu nội dung chat mặc định.

## Live Demo

- Frontend: https://love-sense-ai.vercel.app
- Backend API docs: https://love-sense-ai.onrender.com/docs
- Local frontend mặc định: `http://localhost:3000`
- Local backend mặc định: `http://localhost:8000`

## Screenshot

Ảnh dưới đây dùng dữ liệu minh họa, không phải nội dung chat thật của người dùng.

![Love Sense AI landing page](docs/assets/love-sense-ai-home.png)

## Tính Năng Chính

- Phân tích sắc thái hội thoại từ đoạn chat người dùng nhập thủ công.
- OCR ảnh chụp đoạn chat trên trình duyệt, có bước review/chỉnh sửa trước khi phân tích.
- AI Vision OCR tùy chọn, chỉ chạy khi người dùng đồng ý gửi ảnh đến AI provider.
- Gợi ý phản hồi nhẹ nhàng, tôn trọng, không thao túng.
- Hồ sơ cá nhân hóa cho phong cách giao tiếp và bối cảnh quan hệ.
- Lịch sử phân tích có consent: lưu kết quả và lưu chat gốc là hai lựa chọn riêng.
- Trang privacy để xóa lịch sử, hồ sơ hoặc toàn bộ dữ liệu của user hiện tại.
- Auth email/password với Bearer JWT.
- Dữ liệu profile/history/consent được scope theo `user_id`.
- Output validator, fallback mock an toàn, rate limit cơ bản và benchmark regression cho chất lượng phân tích.

## Tech Stack

Frontend:

- Next.js App Router
- TypeScript
- Tailwind CSS
- React Testing Library + Vitest
- Tesseract.js cho OCR local

Backend:

- FastAPI
- Pydantic / pydantic-settings
- SQLAlchemy async
- PostgreSQL/Supabase trong production
- SQLite fallback cho development/test khi được cấu hình
- Uvicorn

AI:

- LLM provider tương thích OpenAI Chat Completions
- 9Router/OpenRouter-compatible configuration qua `LLM_*`
- Mock mode mặc định an toàn cho test và demo nội bộ
- AI Vision OCR qua endpoint `/api/ocr/vision` khi có consent riêng

## API Overview

Production API docs có tại:

https://love-sense-ai.onrender.com/docs

Các endpoint chính:

- `GET /health`
- `GET /api/health`
- `POST /api/register`
- `POST /api/token`
- `GET /api/me`
- `POST /api/analyze`
- `POST /api/ocr/vision`
- `GET/PUT/DELETE /api/profile`
- `GET/DELETE /api/history`
- `DELETE /api/history/{id}`
- `GET/POST /api/consent`
- `DELETE /api/user-data`

Chi tiết request/response nằm trong [API Documentation](docs/API_DOCUMENTATION.md).

## Firebase Login

Love Sense AI hỗ trợ Google Login bằng Firebase Authentication:

1. Frontend gọi Firebase Web SDK để đăng nhập Google.
2. Firebase trả ID Token cho user đang đăng nhập.
3. Frontend gửi token đến backend qua:

```http
Authorization: Bearer <firebase_id_token>
```

4. Backend FastAPI dùng Firebase Admin SDK để verify token.
5. Backend map `firebase_uid` sang `users.id` nội bộ để profile, history và consent vẫn được scope theo user.

User chưa đăng nhập vẫn dùng được `/api/analyze` để demo, nhưng không được lưu profile/history. Các route profile, history, consent và delete-data yêu cầu đăng nhập.

### Cấu Hình Firebase Console

1. Tạo Firebase project cho Love Sense AI.
2. Vào Authentication -> Sign-in method.
3. Bật Google provider.
4. Vào Authentication -> Settings -> Authorized domains.
5. Thêm:
   - `localhost`
   - `love-sense-ai.vercel.app`
6. Vào Project settings -> General -> Web apps để lấy Firebase Web SDK config.
7. Vào Project settings -> Service accounts để tạo service account JSON cho backend. Không commit JSON này.

### Vercel Env

Đặt trong project frontend trên Vercel:

```text
NEXT_PUBLIC_API_URL=https://love-sense-ai.onrender.com
NEXT_PUBLIC_API_BASE_URL=https://love-sense-ai.onrender.com
NEXT_PUBLIC_FIREBASE_API_KEY=<Firebase web client value>
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=<project>.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=<project-id>
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=<project>.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=<sender-id>
NEXT_PUBLIC_FIREBASE_APP_ID=<app-id>
```

Các biến `NEXT_PUBLIC_FIREBASE_*` là client config public của Firebase Web SDK, không phải backend secret.

### Render Env

Đặt trong backend service trên Render:

```text
APP_ENV=production
FRONTEND_URL=https://love-sense-ai.vercel.app
ALLOWED_ORIGINS=https://love-sense-ai.vercel.app
DATABASE_URL=<Supabase PostgreSQL connection string>
SECRET_KEY=<strong random value>
FIREBASE_SERVICE_ACCOUNT_JSON=<service account JSON string>
LLM_MOCK_MODE=false
```

Không đưa `FIREBASE_SERVICE_ACCOUNT_JSON` vào frontend, GitHub, README hoặc log.

## Privacy Note

Love Sense AI được thiết kế để giảm rủi ro xử lý dữ liệu nhạy cảm:

- Không lưu `chat_text` mặc định.
- `save_result=true` chỉ lưu kết quả tổng hợp nếu user bật lưu lịch sử.
- `save_input=true` mới cho phép lưu nội dung chat gốc.
- Ảnh OCR không được lưu mặc định.
- AI Vision chỉ gửi ảnh lên backend/provider khi user tick consent riêng.
- Không log API key, token, ảnh/base64 hoặc nội dung chat nhạy cảm.
- User có thể xóa lịch sử, hồ sơ hoặc toàn bộ dữ liệu trong trang `/privacy`.
- Kết quả luôn chỉ mang tính tham khảo và không thay thế giao tiếp trực tiếp.

## Chạy Backend Local

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Nếu chưa có PostgreSQL/Supabase ở máy dev, có thể dùng SQLite development fallback theo cấu hình `.env.example`. Production phải đặt `APP_ENV=production`, `DATABASE_URL` PostgreSQL/Supabase và `SECRET_KEY` thật.

## Chạy Frontend Local

```powershell
cd frontend
npm install
npm run dev
```

Mở:

```text
http://localhost:3000
```

Frontend đọc backend URL qua:

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

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

## Demo

Kịch bản demo 3 phút nằm tại [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).

Luồng demo khuyến nghị:

1. Đăng ký hoặc đăng nhập tài khoản demo.
2. Vào `/analyze`, tải ảnh chat minh họa hoặc nhập đoạn chat mẫu.
3. Review nội dung OCR trước khi phân tích.
4. Tick lưu kết quả vào history, không tick lưu chat gốc để minh họa privacy default.
5. Xem `/history`.
6. Vào `/privacy` và xóa dữ liệu demo.

## Tài Liệu

- [Demo Script](docs/DEMO_SCRIPT.md)
- [Setup Guide](SETUP.md)
- [Testing Guide](docs/TESTING.md)
- [Project Guide](docs/PROJECT_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Firebase Auth Guide](docs/AUTH_FIREBASE.md)
- [Privacy Design](docs/PRIVACY_DESIGN.md)
- [OCR and Vision Plan](docs/OCR_AND_VISION_PLAN.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Roadmap](docs/ROADMAP.md)
