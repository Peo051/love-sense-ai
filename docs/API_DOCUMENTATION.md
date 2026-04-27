# API Documentation

Base URL local: `http://localhost:8000`

Các endpoint profile, history, consent và delete data yêu cầu Bearer token. Token có thể là legacy JWT nội bộ ở môi trường dev hoặc Firebase ID Token khi đăng nhập Google:

```http
Authorization: Bearer <firebase_id_token>
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

Trả về user hiện tại theo token. Endpoint này bắt buộc đăng nhập và không trả thông tin nhạy cảm.

Response:

```json
{
  "id": "internal-user-uuid",
  "uid": "firebase-uid-or-internal-user-id",
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "is_active": true
}
```

## POST /api/analyze

Phân tích đoạn chat tình cảm. Mặc định backend dùng mock; khi `LLM_MOCK_MODE=false`, backend gọi provider tương thích OpenAI Chat Completions theo cấu hình `LLM_*` như 9router. Endpoint có thể dùng khi chưa đăng nhập, nhưng chỉ lưu lịch sử khi có Bearer token hợp lệ và có consent lưu dữ liệu.

Backend không log API key, token hoặc `chat_text`. Nếu LLM timeout, lỗi tạm thời hoặc trả lỗi provider, backend retry theo cấu hình rồi fallback mock response an toàn cùng schema.

Sau khi LLM trả kết quả, backend chạy output validator trước khi trả response:

- Chuẩn hóa `evidence` về object `{quote,label,reason}` và bỏ evidence không khớp gần với `chat_text`.
- Giới hạn `confidence` khi đoạn chat quá ngắn, OCR có cảnh báo chất lượng thấp hoặc không có evidence rõ.
- Chuẩn hóa `emotion_distribution` về key không dấu và tổng gần `1.0`.
- Rewrite output nếu provider trả các kết luận không an toàn như “hết yêu”, “phản bội”, “lừa dối” hoặc “chắc chắn”.

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
    "than_mat": 0.0,
    "treu_dua": 0.0,
    "quan_tam": 0.0,
    "met_moi": 0.35,
    "ne_tranh": 0.25,
    "kho_chiu": 0.0,
    "trung_lap": 0.2,
    "chua_du_du_lieu": 0.0,
    "buon": 0.2
  },
  "summary": "Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều. Không đủ dữ liệu để kết luận chắc chắn cảm xúc thật sự.",
  "context_note": "Nếu người này thường im lặng khi mệt, nên phản hồi nhẹ nhàng thay vì hỏi dồn.",
  "suggested_reply": "Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.",
  "warning": "Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.",
  "tone": "mệt mỏi / cần khoảng lặng",
  "evidence": [
    {
      "quote": "Em mệt thôi.",
      "label": "mệt mỏi / né tránh nhẹ",
      "reason": "Câu cho thấy người nói mệt hoặc muốn lùi lại khỏi cuộc trò chuyện lúc đó."
    }
  ],
  "uncertainty_reasons": ["Chỉ dựa trên vài câu chat nên chưa thể kết luận chắc chắn."],
  "input_quality": "medium",
  "reply_style": "nhẹ nhàng, cho không gian, không hỏi dồn",
  "authenticated": true,
  "saved_to_history": true
}
```

Các field `tone`, `evidence`, `uncertainty_reasons`, `input_quality`, `reply_style`, `authenticated`, `saved_to_history` là phần mở rộng tương thích ngược. Frontend có thể dùng để hiển thị căn cứ phân tích, trạng thái lưu lịch sử và cảnh báo khi input đến từ OCR hoặc còn thiếu dữ liệu. `evidence` dùng object `{quote,label,reason}` để mỗi nhận định quan trọng có câu chat làm căn cứ.

Lỗi thường gặp:

- `400`: thiếu hoặc rỗng `chat_text`, hoặc nội dung không phù hợp với safety filter.
- `429`: vượt rate limit, response có `Retry-After`.
- `500`: lỗi ngoài dự kiến. Không trả secret hoặc cấu hình nhạy cảm.

Rate limit mặc định: 20 request / 60 giây, cấu hình bằng `RATE_LIMIT_MAX_REQUESTS` và `RATE_LIMIT_WINDOW_SECONDS`. Nếu đã đăng nhập thì tính theo `user_id`; nếu chưa đăng nhập thì tính theo IP client.

## POST /api/ocr/vision

Trích xuất nội dung chữ từ ảnh chụp đoạn chat bằng AI Vision. Endpoint này chỉ dùng khi user đã bật tùy chọn AI Vision và đồng ý gửi ảnh đến AI provider.

Backend không lưu ảnh, không log ảnh/base64 và không tự động tạo lịch sử phân tích. Sau khi nhận text, frontend vẫn yêu cầu user review/chỉnh sửa trước khi gọi `/api/analyze`.

Model vision được chọn bằng `VISION_MODEL`; nếu biến này trống, backend dùng `LLM_MODEL`. Backend vẫn đọc alias cũ `VISION_OCR_MODEL` để tương thích môi trường cũ. Không cấu hình `LLM_API_KEY` trong frontend.

Request multipart:

- `image`: file PNG, JPG, JPEG hoặc WEBP, tối đa 5MB.
- `is_accepted`: `true`.

Response:

```json
{
  "text": "A: anh iu ngủ ngon nhó\nB: yeuemm",
  "confidence": 91,
  "warnings": [],
  "provider": "vision"
}
```

Lỗi thường gặp:

- `400`: chưa consent, file rỗng, file không phải ảnh hoặc ảnh quá lớn.
- `503`: `LLM_MOCK_MODE=true` hoặc thiếu cấu hình như `LLM_API_KEY`. Ví dụ: `AI Vision đang tắt trong cấu hình backend.` hoặc `Missing LLM_API_KEY for AI Vision.`
- `502`: Vision provider timeout/lỗi hoặc model không hỗ trợ ảnh. Ví dụ: `Current model does not support image input.` Frontend nên fallback về OCR local/manual input.

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

## Related Docs

- [Privacy Design](PRIVACY_DESIGN.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Setup Guide](../SETUP.md)
