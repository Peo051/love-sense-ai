# Firebase Authentication Guide

Tài liệu này mô tả cách Love Sense AI dùng Firebase Google Login cho frontend Next.js và backend FastAPI.

## Kiến Trúc Auth

Love Sense AI có hai lớp định danh:

- Firebase Authentication: xác thực Google Login và cấp Firebase ID Token.
- Backend database: lưu dữ liệu theo `users.id` nội bộ để profile, history và consent luôn scoped theo user.

Backend thêm cột `users.firebase_uid` để map Firebase uid sang internal user id. Khi một Firebase user gọi API lần đầu, backend sẽ:

1. Verify Firebase ID Token bằng Firebase Admin SDK.
2. Tìm user theo `firebase_uid`.
3. Nếu chưa có, tìm user theo email để link tài khoản cũ nếu phù hợp.
4. Nếu vẫn chưa có, tạo user nội bộ mới với `firebase_uid`.
5. Dùng `users.id` nội bộ cho profile/history/consent.

Luồng email/password JWT cũ vẫn được giữ để không phá test và các tài khoản dev hiện có.

## Flow Đăng Nhập

1. User mở `/login`.
2. Frontend gọi `loginWithGoogle()` từ `frontend/lib/auth.ts`.
3. Firebase Web SDK mở Google popup.
4. Sau khi đăng nhập thành công, `AuthProvider` trong `frontend/contexts/AuthContext.tsx` lưu user state.
5. `getToken()` gọi `getIdToken(auth.currentUser, true)` để lấy Firebase ID Token mới.
6. API client tự thêm header:

```http
Authorization: Bearer <firebase_id_token>
```

7. Backend verify token và map user trước khi xử lý route cần đăng nhập.

## Flow Gọi API Có Token

Frontend API client nằm ở `frontend/lib/api.ts`.

- Nếu user đã đăng nhập Firebase, `setAuthTokenProvider()` dùng token từ `AuthContext`.
- Nếu chưa đăng nhập, request public như `/api/analyze` vẫn chạy mà không gửi `Authorization`.
- Nếu còn legacy token trong localStorage, API client vẫn gửi token đó để giữ tương thích dev.

Route public:

- `POST /api/analyze`: cho phép dùng thử không đăng nhập. Nếu không có token hợp lệ thì không lưu history.

Route yêu cầu đăng nhập:

- `GET /api/me`
- `GET/POST/DELETE /api/profile`
- `GET/DELETE /api/history`
- `GET/DELETE /api/history/{id}`
- `GET/POST /api/consent`
- `DELETE /api/user-data`

## Backend Verify Token

Các file chính:

- `backend/app/core/firebase.py`: khởi tạo Firebase Admin SDK từ `FIREBASE_SERVICE_ACCOUNT_JSON`.
- `backend/app/deps/auth.py`: verify Bearer token, hỗ trợ Firebase ID Token và legacy JWT.
- `backend/app/routes/auth.py`: `GET /api/me`.

Backend không đọc service account từ file trong repo. Production phải cấu hình credential JSON bằng biến môi trường `FIREBASE_SERVICE_ACCOUNT_JSON` trên Render.

Nếu `APP_ENV=production` và thiếu credential JSON, backend sẽ báo lỗi cấu hình rõ ràng khi startup.

## Cách Test `/api/me`

Sau khi đăng nhập ở frontend, mở browser console:

```js
const user = window.firebaseAuth?.currentUser
```

Nếu app không expose `firebaseAuth` ra global, có thể test bằng cách thêm tạm breakpoint trong `AuthContext.getToken()` hoặc copy token từ tab Network của request đã đăng nhập. Không commit thay đổi debug.

Gọi API:

```bash
curl -H "Authorization: Bearer <firebase_id_token>" https://love-sense-ai.onrender.com/api/me
```

Kỳ vọng response:

```json
{
  "id": "internal-user-uuid",
  "uid": "firebase-uid",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "is_active": true
}
```

Không token:

```bash
curl -i https://love-sense-ai.onrender.com/api/me
```

Kỳ vọng `401`.

## Token Hết Hạn

Firebase ID Token có thời hạn ngắn. Frontend gọi:

```ts
getIdToken(auth.currentUser, true)
```

để lấy token mới trước khi gọi backend. Nếu token vẫn bị từ chối:

1. Đăng xuất.
2. Đăng nhập lại.
3. Kiểm tra đồng hồ hệ thống.
4. Kiểm tra `FIREBASE_SERVICE_ACCOUNT_JSON` trên Render có thuộc đúng Firebase project.

## Cấu Hình Firebase Console

1. Firebase Console -> Authentication -> Sign-in method.
2. Enable Google provider.
3. Authentication -> Settings -> Authorized domains.
4. Thêm:
   - `localhost`
   - `love-sense-ai.vercel.app`
5. Project settings -> General -> Web apps để lấy frontend config.
6. Project settings -> Service accounts để tạo credential JSON cho backend.

## Env Cần Cấu Hình

Frontend Vercel:

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

Backend Render:

```text
APP_ENV=production
FRONTEND_URL=https://love-sense-ai.vercel.app
ALLOWED_ORIGINS=https://love-sense-ai.vercel.app
DATABASE_URL=<Supabase PostgreSQL connection string>
SECRET_KEY=<strong random value>
FIREBASE_SERVICE_ACCOUNT_JSON=<service account JSON string>
```

Không cấu hình Firebase Admin credential ở Vercel frontend.

## Lỗi Thường Gặp

### `auth/unauthorized-domain`

Google popup bị Firebase chặn vì domain frontend chưa được thêm vào Authorized domains.

Cách xử lý:

- Thêm `localhost` cho local dev.
- Thêm `love-sense-ai.vercel.app` cho production.
- Nếu dùng preview domain Vercel, thêm preview domain đó hoặc test bằng production domain chính.

### `Missing FIREBASE_SERVICE_ACCOUNT_JSON`

Backend production thiếu credential JSON.

Cách xử lý:

- Đặt `FIREBASE_SERVICE_ACCOUNT_JSON` trong Render Environment.
- Dán JSON một dòng hoặc dùng secret manager hỗ trợ multiline.
- Restart backend service sau khi cập nhật env.

### `Invalid or expired authentication token`

Backend không verify được token.

Cách xử lý:

- Đảm bảo frontend gửi header `Authorization: Bearer <firebase_id_token>`.
- Đăng xuất và đăng nhập lại để refresh token.
- Kiểm tra service account backend thuộc cùng Firebase project với frontend config.
- Không dùng Firebase Web config thay cho service account backend.

### CORS blocked `Authorization` header

Browser chặn request vì backend CORS chưa cho frontend domain hoặc header.

Cách xử lý:

- Render env phải có `FRONTEND_URL=https://love-sense-ai.vercel.app`.
- Nếu dùng `ALLOWED_ORIGINS`, thêm đúng frontend origin.
- Backend `allow_headers` phải cho `Authorization`; hiện app dùng `allow_headers=["*"]`.

## Privacy Và Bảo Mật

- Không commit `.env`, `.env.local`, service account JSON, token hoặc secret.
- Không đưa backend credential vào frontend.
- Không log Firebase ID Token.
- Không log nội dung chat, ảnh OCR hoặc base64.
- `/api/analyze` không lưu history nếu user chưa đăng nhập hoặc chưa bật consent.
- `chat_text` chỉ được lưu khi `save_input=true`.
