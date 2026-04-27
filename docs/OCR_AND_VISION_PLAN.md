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

## Vision AI sau MVP

Vision AI có thể chính xác hơn OCR truyền thống vì mô hình hiểu layout bong bóng chat, emoji và thứ tự hội thoại tốt hơn. Tuy nhiên hướng này yêu cầu gửi ảnh lên backend hoặc provider AI, nên chỉ nên triển khai khi có cơ chế consent rõ ràng.

Nếu thêm Vision AI sau này, cần:

- Consent riêng trước khi gửi ảnh ra backend/provider.
- Giải thích rõ ảnh được xử lý ở đâu.
- Không lưu ảnh mặc định.
- Xóa ảnh ngay sau xử lý nếu không có consent lưu riêng.
- Không log ảnh, URL ảnh, base64 hoặc OCR text nhạy cảm.
- Giữ fallback nhập thủ công nếu người dùng không đồng ý gửi ảnh.
- Tách riêng thiết lập retention cho ảnh, OCR text và kết quả phân tích.

## API đề xuất sau MVP

Không cần thay đổi `/api/analyze` cho MVP OCR local. Nếu thêm Vision AI, nên tạo endpoint riêng, ví dụ:

- `POST /api/ocr/vision`
- Request yêu cầu consent rõ ràng.
- Response chỉ trả text đã trích xuất và cảnh báo chất lượng.
- Không tự động tạo lịch sử phân tích.

Luồng phân tích vẫn nên giữ:

1. Người dùng tải ảnh.
2. Hệ thống trích xuất text.
3. Người dùng review/chỉnh sửa.
4. Người dùng bấm phân tích.
5. Chỉ lưu dữ liệu theo consent hiện có.
