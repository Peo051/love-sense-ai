# Demo Script: Love Sense AI

Tài liệu này dùng cho demo public khoảng 3 phút. Không sử dụng ảnh chat thật, tài khoản cá nhân thật hoặc dữ liệu nhạy cảm trong lúc demo.

## Chuẩn Bị Trước Demo

- Frontend: https://love-sense-ai.vercel.app
- Backend API docs: https://love-sense-ai.onrender.com/docs
- Chuẩn bị một tài khoản demo mới hoặc tạo tài khoản ngay trong demo.
- Chuẩn bị một ảnh chat minh họa không chứa thông tin cá nhân. Nếu chưa có ảnh, dùng đoạn chat mẫu ở cuối tài liệu và nhập thủ công.
- Không dùng API key, `.env`, token hoặc thông tin production secret trong màn hình trình chiếu.

## Kịch Bản 3 Phút

### 0:00 - 0:25: Giới Thiệu Ngắn

Mở trang chủ:

```text
https://love-sense-ai.vercel.app
```

Nói ngắn gọn:

- Love Sense AI hỗ trợ phân tích sắc thái hội thoại và gợi ý phản hồi tham khảo.
- Người dùng chủ động nhập nội dung hoặc tải ảnh để OCR.
- Ứng dụng không tự truy cập tin nhắn và không lưu chat mặc định.
- Kết quả chỉ hỗ trợ giao tiếp bình tĩnh hơn, không kết luận chắc chắn cảm xúc của người khác.

### 0:25 - 0:55: Đăng Ký Hoặc Đăng Nhập

1. Vào `/auth`.
2. Chọn đăng ký hoặc đăng nhập bằng tài khoản demo.
3. Sau khi đăng nhập, nhấn vào trang `/analyze`.

Điểm cần nói:

- Tài khoản giúp tách dữ liệu hồ sơ, lịch sử và consent theo từng user.
- User này không thể xem dữ liệu của user khác.

### 0:55 - 1:35: Upload Ảnh OCR Và Review Text

1. Tại `/analyze`, mở section nhập từ ảnh chụp đoạn chat.
2. Tải ảnh chat minh họa.
3. Nhấn `Trích xuất chữ từ ảnh`.
4. Chờ OCR local hoặc AI Vision nếu backend demo đã bật và user tick consent riêng.
5. Review khu vực `Bản nháp nội dung trích xuất`.
6. Chỉnh lại text nếu OCR nhận diện sai.
7. Chọn `Thay thế đoạn chat hiện tại` hoặc `Dùng nội dung này`.

Điểm cần nói:

- OCR có thể sai, nên luôn có bước review trước khi phân tích.
- Ảnh không được lưu mặc định.
- AI Vision chỉ gửi ảnh lên provider khi user đồng ý riêng.
- Người dùng có thể che hoặc xóa thông tin nhạy cảm trước khi phân tích.

### 1:35 - 2:05: Phân Tích Hội Thoại

1. Bổ sung bối cảnh cá nhân hóa, ví dụ:

```text
Người ấy thường dùng cách nói trêu đùa khi thân mật. Nếu mệt thì hay trả lời ngắn.
```

2. Tick `Lưu kết quả phân tích vào lịch sử`.
3. Không tick `Lưu nội dung chat gốc` để minh họa privacy default.
4. Nhấn `Phân tích sắc thái`.
5. Chờ result panel hiển thị.

Điểm cần chỉ ra:

- Cảm xúc tổng quan.
- Độ tin cậy.
- Phân bố cảm xúc.
- Câu làm căn cứ nếu có.
- Gợi ý phản hồi.
- Cảnh báo `Kết quả chỉ mang tính tham khảo`.

### 2:05 - 2:35: Xem History

1. Vào `/history`.
2. Tìm item vừa phân tích.
3. Mở chi tiết nếu UI có detail panel.
4. Chỉ ra rằng kết quả tổng hợp được lưu, nhưng chat gốc không xuất hiện nếu chưa consent `save_input=true`.

Điểm cần nói:

- Lịch sử scoped theo user hiện tại.
- Lưu kết quả và lưu chat gốc là hai consent riêng.
- Người dùng có thể xóa từng item.

### 2:35 - 3:00: Xóa Dữ Liệu

1. Vào `/privacy`.
2. Giải thích các nhóm dữ liệu:
   - Hồ sơ cá nhân hóa.
   - Lịch sử phân tích.
   - Consent settings.
3. Nhấn xóa lịch sử hoặc xóa toàn bộ dữ liệu demo.
4. Xác nhận trong dialog.
5. Quay lại `/history` để kiểm tra dữ liệu đã được xóa.

Điểm cần nói:

- Các hành động xóa có confirm để tránh bấm nhầm.
- Xóa dữ liệu chỉ áp dụng cho user hiện tại.
- Đây là điểm quan trọng cho demo privacy-first.

## Đoạn Chat Mẫu Nếu Không Có Ảnh

```text
A: Em sao vậy?
B: Không sao.
A: Anh thấy em hơi lạ.
B: Em mệt thôi.
```

Bối cảnh:

```text
Người ấy thường im lặng khi mệt, không thích bị hỏi dồn.
```

Kỳ vọng kết quả:

- Sắc thái có thể nghiêng về mệt mỏi / né tránh nhẹ.
- Confidence không nên quá cao vì đoạn chat ngắn.
- Suggested reply nên nhẹ nhàng, không ép đối phương giải thích ngay.

## Checklist Sau Demo

- Đăng xuất khỏi tài khoản demo nếu dùng máy chung.
- Xóa dữ liệu demo trong `/privacy`.
- Không để token, `.env`, API key hoặc dashboard production xuất hiện trên màn hình.
- Không dùng ảnh chat thật của người dùng trong tài liệu, slide hoặc recording.
