# OCR And Vision Plan

## MVP hiện tại

Love Sense AI xử lý ảnh chụp đoạn chat bằng OCR chạy trên trình duyệt với `tesseract.js`.

- Người dùng tự tải ảnh lên.
- Ảnh không được gửi lên backend trong MVP.
- Ảnh không được lưu mặc định.
- Nội dung OCR được đưa vào ô nhập đoạn chat để người dùng kiểm tra và chỉnh sửa trước khi phân tích.
- Kết quả OCR có thể sai khi ảnh mờ, chữ nhỏ, nền nhiều họa tiết, emoji hoặc bong bóng chat phức tạp.

## Nguyên tắc quyền riêng tư

- Không tự động lưu ảnh.
- Không lưu nội dung OCR nếu người dùng chưa bật consent phù hợp.
- Không tự động phân tích ngay sau OCR.
- Không log ảnh, base64 ảnh, nội dung chat hoặc dữ liệu nhạy cảm.
- Người dùng nên che hoặc xóa thông tin nhạy cảm trước khi gửi phân tích.

## Chế độ AI Vision nâng cao

Mặc định Love Sense AI vẫn dùng OCR local trên trình duyệt. Người dùng có thể bật tùy chọn "Dùng AI Vision để trích xuất chính xác hơn" khi ảnh có chữ nhỏ, nền nhiều họa tiết, emoji hoặc bong bóng chat khó đọc.

AI Vision yêu cầu consent riêng vì ảnh sẽ được gửi đến backend và AI provider:

- Checkbox bắt buộc: "Tôi đồng ý gửi ảnh này đến AI provider để trích xuất nội dung."
- Backend chỉ đọc ảnh trong bộ nhớ cho request hiện tại.
- Không lưu ảnh mặc định.
- Không log ảnh, URL ảnh, base64 hoặc OCR text nhạy cảm.
- Nếu Vision API lỗi, frontend fallback về OCR local hoặc người dùng nhập thủ công.
- Nếu `LLM_MOCK_MODE=true`, backend trả rõ: "AI Vision đang tắt trong cấu hình backend." và frontend hiển thị lý do này trước khi fallback OCR local.
- Nếu thiếu `LLM_API_KEY`, backend trả rõ: "Missing LLM_API_KEY for AI Vision."
- Nếu provider báo model không hỗ trợ ảnh, backend trả rõ: "Current model does not support image input."
- Sau khi Vision AI trả text, người dùng vẫn phải review/chỉnh sửa trước khi phân tích.
- Tách riêng thiết lập retention cho ảnh, OCR text và kết quả phân tích.

## Cấu hình môi trường

AI Vision dùng cùng cấu hình OpenAI-compatible với luồng phân tích:

```text
LLM_PROVIDER=openai
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=
LLM_MODEL=openai/gpt-4o-mini
VISION_MODEL=openai/gpt-4o-mini
LLM_MOCK_MODE=true
```

`VISION_MODEL` là tùy chọn. Nếu không đặt, backend dùng `LLM_MODEL`. Backend vẫn đọc alias cũ `VISION_OCR_MODEL` để không phá môi trường đã cấu hình trước đó.

## API hiện tại

Không thay đổi `/api/analyze`. Vision AI dùng endpoint riêng:

- `POST /api/ocr/vision`
- Request multipart gồm `image` và `is_accepted=true`.
- Response chỉ trả text đã trích xuất, độ tin cậy và cảnh báo chất lượng.
- Không tự động tạo lịch sử phân tích.
- Không lưu ảnh.

Luồng phân tích vẫn nên giữ:

1. Người dùng tải ảnh.
2. Hệ thống trích xuất text.
3. Người dùng review/chỉnh sửa.
4. Người dùng bấm phân tích.
5. Chỉ lưu dữ liệu theo consent hiện có.
