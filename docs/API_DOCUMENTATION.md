# API Documentation

Base URL local: `http://localhost:8000`

## GET /health

Kiểm tra backend đang chạy.

```json
{
  "status": "healthy",
  "service": "Love Emotion API"
}
```

## POST /api/analyze

Phân tích mock đoạn chat tình cảm. Backend không lưu mặc định.

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

`POST /api/profile` lưu hồ sơ người dùng và hồ sơ người yêu trong bộ nhớ tạm. Chiều cao, cân nặng và ngoại hình là tùy chọn, không dùng để suy luận cảm xúc.

## History

- `GET /api/history`
- `GET /api/history/{id}`
- `DELETE /api/history/{id}`
- `DELETE /api/history`

Lịch sử chỉ được tạo khi request phân tích có `save_result = true` hoặc `save_input = true`. `chat_text` chỉ được lưu khi `save_input = true`.

## Consent

- `GET /api/consent`
- `POST /api/consent`

Các trường chính:

- `save_input`
- `save_result`
- `consent_type`
- `is_accepted`
- `accepted_at`
- `history_enabled`

## Delete Data

- `DELETE /api/user-data`

Xóa toàn bộ dữ liệu in-memory: hồ sơ, lịch sử và trạng thái consent.
