# Love Sense AI Frontend

Frontend Next.js cho Love Sense AI. Ứng dụng dùng Firebase Google Login, gọi backend FastAPI qua `NEXT_PUBLIC_API_BASE_URL`/`NEXT_PUBLIC_API_URL` và giữ nguyên demo mode cho `/analyze` khi user chưa đăng nhập.

## Công Nghệ

- Next.js App Router
- React + TypeScript
- Tailwind CSS
- Firebase Web SDK
- Tesseract.js cho OCR local
- Vitest + React Testing Library

## Cài Đặt

```powershell
npm install
copy .env.example .env.local
```

Điền Firebase Web SDK config vào `.env.local` nếu muốn test Google Login.

## Chạy Development

```powershell
npm run dev
```

Mở `http://localhost:3000`.

## Biến Môi Trường

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
```

Trên Vercel production, đặt cả hai biến về backend Render:

```text
NEXT_PUBLIC_API_BASE_URL=https://love-sense-ai.onrender.com
NEXT_PUBLIC_API_URL=https://love-sense-ai.onrender.com
```

Không đưa backend secret, database URL hoặc Firebase service account vào frontend.

## Auth

- `/login` dùng Firebase Google Login.
- Frontend lấy Firebase ID Token bằng `getIdToken()` và gửi qua `Authorization: Bearer <token>`.
- `/analyze` vẫn dùng thử được khi chưa đăng nhập, nhưng không lưu lịch sử.
- `/profile`, `/history`, `/privacy` yêu cầu user đăng nhập.

## Kiểm Tra

```powershell
npm run test
npm run typecheck
npm run build
npm audit
```
