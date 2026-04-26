# API Documentation

Base URL local: `http://localhost:8000`

Các endpoint profile, history, consent và delete data yêu cầu header:

```http
Authorization: Bearer <access_token>
```

## GET /health

Kiểm tra backend đang chạy.

```json
{
  "status": "healthy",
  "service": "Love Emotion API"
}
```

## Auth

### POST /api/register

Tạo user mới.

```json
{
  "email": "user@example.com",
  "password": "secret123"
}
```

Response:

```json
{
  "id": "uuid",
  "email": "user@example.com",
  "is_active": true
}
```

### POST /api/token

Đăng nhập bằng OAuth2 password form:

```text
username=user@example.com
password=secret123
```

Response:

```json
{
  "access_token": "jwt",
  "token_type": "bearer"
}
```

### GET /api/me

Trả về user hiện tại theo token.

## POST /api/analyze

Phân tích mock đoạn chat tình cảm. Endpoint có thể dùng khi chưa đăng nhập, nhưng chỉ lưu lịch sử khi có Bearer token và có consent hợp lệ.

Request:

```json
{
  "chat_text": "Em sao vậy?\nKhông sao.\nAnh thấy em hơi lạ.\nEm mệt thôi.",
  "profile_context": "Người yêu thường im lặng khi mệt, không thích bị hỏi dồn.",
  "save_input": false,
  "save_result": true
}
```

Response:

```json
{
  "overall_emotion": "mệt mỏi / né tránh nhẹ",
  "confidence": 0.72,
  "emotion_distribution": {
    "mệt_mỏi": 0.35,
    "né_tránh": 0.25,
    "buồn": 0.2,
    "trung_lập": 0.2
  },
  "summary": "Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều. Không đủ dữ liệu để kết luận chắc chắn cảm xúc thật sự.",
  "context_note": "Nếu người này thường im lặng khi mệt, nên phản hồi nhẹ nhàng thay vì hỏi dồn.",
  "suggested_reply": "Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.",
  "warning": "Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp."
}
```

## Profile

- `GET /api/profile`
- `POST /api/profile`
- `DELETE /api/profile`

`POST /api/profile` lưu hồ sơ người dùng và hồ sơ người yêu cho user đang đăng nhập. Chiều cao, cân nặng và ngoại hình là tùy chọn, không dùng để suy luận cảm xúc.

## History

- `GET /api/history`
- `GET /api/history/{id}`
- `DELETE /api/history/{id}`
- `DELETE /api/history`

History luôn được lọc theo user đang đăng nhập. `chat_text` chỉ được trả về khi user đã bật lưu nội dung chat tại thời điểm phân tích.

## Consent

- `GET /api/consent`
- `POST /api/consent`

Các trường chính:

- `history_enabled`
- `save_input`
- `save_result`
- `consent_type`
- `is_accepted`
- `accepted_at`

## Delete Data

- `DELETE /api/user-data`

Xóa hồ sơ, lịch sử và trạng thái consent của user đang đăng nhập. Endpoint này không xóa tài khoản `users`.
