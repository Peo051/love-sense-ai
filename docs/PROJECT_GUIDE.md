# Project Guide

Love Emotion Web là web app phân tích sắc thái cảm xúc trong đoạn hội thoại tình cảm theo hướng hỗ trợ giao tiếp nhẹ nhàng.

## Luồng MVP

1. Người dùng nhập đoạn chat thủ công.
2. Người dùng nhập bối cảnh cá nhân hóa.
3. Frontend gửi request đến FastAPI backend.
4. Backend validate dữ liệu và kiểm tra safety đơn giản.
5. Mock AI service sinh kết quả phân tích.
6. Frontend hiển thị kết quả, phân bố cảm xúc, gợi ý phản hồi và cảnh báo.

## Quyền riêng tư

MVP không lưu nội dung chat. Tùy chọn `save_input` đã có trong API contract nhưng backend chưa ghi database. Khi mở tính năng lịch sử, cần bổ sung xác nhận đồng ý lưu, quyền xóa dữ liệu và tài liệu rõ ràng.

## Cách phát triển tiếp

Ưu tiên hoàn thiện chất lượng MVP trước khi thêm database hoặc LLM thật. Mỗi bước mở rộng nên giữ nguyên contract an toàn: không theo dõi, không thao túng, không kết luận chắc chắn.
