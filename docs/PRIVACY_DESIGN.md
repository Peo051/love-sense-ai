# Privacy Design

Love Sense AI ưu tiên phân tích do người dùng chủ động nhập, không đọc trộm Zalo, Messenger, SMS, notification hoặc danh bạ.

## Dữ Liệu Có Thể Lưu

- `users`: email đăng nhập và password đã hash.
- `profiles`: hồ sơ người dùng theo `user_id`.
- `partner_profiles`: hồ sơ người yêu theo `user_id`.
- `consents`: cài đặt quyền riêng tư theo `user_id` và `consent_type`.
- `analysis_sessions`: lịch sử kết quả phân tích theo `user_id`.

## Nguyên Tắc Chat Text

- Không lưu `chat_text` mặc định.
- Chỉ lưu `chat_text` khi request có `save_input=true` và user đã đăng nhập.
- Nếu chỉ `save_result=true`, chỉ lưu kết quả tổng hợp: cảm xúc, độ tin cậy, phân bố cảm xúc, tóm tắt, gợi ý phản hồi và cảnh báo.
- Database có check constraint để `chat_text` chỉ tồn tại khi `save_input=true` và consent đã được chấp nhận.

## Consent

Người dùng có quyền:

- Bật/tắt lưu lịch sử.
- Bật/tắt lưu kết quả phân tích.
- Bật/tắt lưu nội dung chat.
- Không bị ép đồng ý lưu dữ liệu.

Các trường consent chính:

- `history_enabled`
- `save_input`
- `save_result`
- `consent_type`
- `is_accepted`
- `accepted_at`

## Delete Data

Các endpoint xóa dữ liệu chỉ áp dụng cho user đang đăng nhập:

- `DELETE /api/history/{id}`: xóa một lịch sử của user hiện tại.
- `DELETE /api/history`: xóa toàn bộ lịch sử của user hiện tại.
- `DELETE /api/profile`: xóa hồ sơ cá nhân hóa của user hiện tại.
- `DELETE /api/user-data`: xóa profile, partner profile, preferences, consent và history của user hiện tại.

User A không thể đọc, sửa hoặc xóa dữ liệu của User B vì mọi truy vấn đều lọc theo `current_user.id`.

## Logging

Backend và frontend không được log:

- API key.
- Bearer token.
- `chat_text` đầy đủ.
- Nội dung profile riêng tư.

Nếu cần debug, chỉ log metadata không nhạy cảm như provider, model, mock mode, status code hoặc request id.

## Related Docs

- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Setup Guide](../SETUP.md)
