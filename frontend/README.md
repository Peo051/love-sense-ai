# Love Emotion Frontend

Frontend Next.js cho Love Emotion Web.

## Công Nghệ

- Next.js
- React
- TypeScript
- Tailwind CSS
- lucide-react
- Vitest + React Testing Library

## Cài Đặt

```powershell
npm install
```

## Chạy Development

```powershell
npm run dev
```

Mở `http://localhost:3000/analyze`.

## Biến Môi Trường

Tạo `.env.local` nếu backend không chạy ở cổng mặc định:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Auth

Trang `/auth` cho phép đăng ký và đăng nhập. Token được lưu trong `localStorage` và tự động gắn vào request profile, history, consent và delete data.

## Kiểm Tra

```powershell
npm run test
npm run typecheck
npm run build
npm audit
```
