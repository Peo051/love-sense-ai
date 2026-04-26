# Love Emotion Web - Project Guide

## Mục Tiêu

Love Emotion Web hỗ trợ phân tích sắc thái cảm xúc trong đoạn chat tình cảm do người dùng nhập thủ công. Ứng dụng đưa ra nhận định tham khảo, gợi ý phản hồi nhẹ nhàng và cảnh báo an toàn.

## Luồng Hiện Tại

Người dùng đăng ký/đăng nhập → nhập đoạn chat và bối cảnh cá nhân hóa → frontend gửi `POST /api/analyze` → backend validate và gọi mock AI → backend chỉ lưu lịch sử khi user có consent → frontend hiển thị kết quả.

## Nguyên Tắc An Toàn

- Không đọc trộm tin nhắn hoặc dữ liệu thiết bị.
- Không kết luận chắc chắn cảm xúc của người khác.
- Không đưa lời khuyên thao túng.
- Không lưu nội dung chat mặc định.
- Luôn hiển thị cảnh báo: “Kết quả chỉ mang tính tham khảo, không thể thay thế giao tiếp trực tiếp.”

## Thành Phần Chính

- `frontend/app/analyze/page.tsx`: form phân tích và hiển thị kết quả.
- `frontend/app/auth/page.tsx`: đăng ký, đăng nhập và lưu Bearer token local.
- `frontend/app/profile/page.tsx`: hồ sơ cá nhân hóa.
- `frontend/app/history/page.tsx`: lịch sử phân tích theo user.
- `frontend/app/privacy/page.tsx`: consent và xóa dữ liệu.
- `backend/app/routes/analyze.py`: endpoint phân tích, có optional auth để lưu lịch sử.
- `backend/app/routes/auth.py`: đăng ký, đăng nhập, `/api/me`.
- `backend/app/services/db_store.py`: repository cho profile/history/consent.
- `backend/app/models/`: SQLAlchemy models.
- `database/schema.sql`: schema PostgreSQL/Supabase mới.
- `database/migrations/`: SQL migrations theo thứ tự.

## Database Và Auth

Backend dùng PostgreSQL/Supabase qua SQLAlchemy async. Profile, partner profile, history và consent đều có `user_id`; routes yêu cầu đăng nhập luôn lọc theo `current_user.id`.

`POST /api/analyze` vẫn chạy khi chưa đăng nhập, nhưng không lưu lịch sử nếu không có token hoặc không có consent hợp lệ.

## Việc Tiếp Theo

- Kiểm tra migration trên PostgreSQL/Supabase thật.
- Làm UX đăng nhập rõ hơn cho các trang cần token.
- Thêm integration test dùng database thật hoặc container.
- Sau đó mới tích hợp LLM thật bằng biến môi trường.
