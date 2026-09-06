# Thiết Kế Quyền Riêng Tư & Lịch Sử (Privacy & History Design)

CodeSense AI Tutor ưu tiên bảo vệ tối đa quyền riêng tư của sinh viên trong quá trình thực hành lập trình C# OOP. Hệ thống hoạt động dựa trên dữ liệu do sinh viên chủ động cung cấp, trao quyền kiểm soát minh bạch và không ép buộc consent.

---

## 1. Nguyên Tắc Cốt Lõi Về Mã Nguồn & Dữ Liệu Đầu Vào

### 1.1. Mặc Định Không Lưu Mã Nguồn (Default: Student Code Is NOT Stored)
- Mặc định hệ thống **KHÔNG lưu trữ mã nguồn học viên** (`student_code`) vào cơ sở dữ liệu.
- Cơ sở dữ liệu kích hoạt Check Constraint nghiêm ngặt:
  - `ck_analysis_sessions_chat_text_requires_consent`: `chat_text IS NULL OR (save_input IS TRUE AND is_accepted IS TRUE)`
  - `ck_student_attempts_code_requires_consent`: `student_code IS NULL OR save_input IS TRUE`

### 1.2. Phân Định Giữa `save_result` và `save_input`

| Thuộc Tính | Mục Đích & Phạm Vi Dữ Liệu Được Lưu | Mặc Định |
| :--- | :--- | :--- |
| **`save_result`** | **Lưu kết quả phân tích sư phạm:**<br>- Chẩn đoán kỹ thuật (`diagnosis`: loại lỗi, phân loại, độ nghiêm trọng, giải thích sư phạm)<br>- Kỹ năng liên quan (`knowledge_components` thuộc taxonomy C# OOP)<br>- Tiến trình gợi ý (`hint_level`, `highest_hint_level_used`, `solution_revealed`)<br>- Trạng thái giải quyết (`success_state`)<br>- Tóm tắt sư phạm (`summary`) và hành động tiếp theo (`next_action`) | Bật khi bật lưu lịch sử (`true`) |
| **`save_input`** | **Cho phép lưu dữ liệu đầu vào gốc khi có sự đồng ý tường minh:**<br>- Đề bài bài tập (`problem_statement`)<br>- Mã nguồn sinh viên (`student_code`)<br>- Lỗi biên dịch (`compiler_error`)<br>*Ghi chú:* Khi `save_input=false`, tuyệt đối không lưu các trường này vào DB và không đính kèm vào `context_note`. | Luôn TẮT (`false`) |

---

## 2. Mô Hình Dữ Liệu Thuộc Sở Hữu Người Dùng

Mọi dữ liệu cá nhân được phân định rõ ràng và gắn chặt với `user_id`:
1. `users`: Tài khoản xác thực (email và mật khẩu đã băm bằng bcrypt).
2. `student_profiles`: Hồ sơ học tập cá nhân hóa (trình độ, khóa học, phong cách giải thích).
3. `learning_sessions`: Phiên học tập đa lượt (multi-turn) gồm nhiều lần thử bài và trao đổi.
4. `student_attempts`: Từng lần nộp bài/thử lại trong phiên (lưu chẩn đoán, gợi ý; code chỉ lưu khi `save_input=true`).
5. `tutor_messages`: Chuỗi tin nhắn hội thoại sư phạm đã được làm sạch.
6. `student_skill_mastery`: Bảng theo dõi mức độ thành thạo các kỹ năng OOP theo công thức tất định.
7. `student_mastery_audit`: Bản ghi kiểm toán từng bước cập nhật điểm thành thạo kèm lý do và attempt liên kết.
8. `analysis_sessions`: Lịch sử các phiên phân tích đơn lẻ từ trang Gia sư AI.
9. `consents`: Cài đặt quyền riêng tư và trạng thái chấp thuận của từng loại tác vụ.

---

## 3. Trích Xuất Ảnh Bằng OCR và AI Vision Cho Lập Trình

- **Local OCR (Mặc định bảo vệ riêng tư):** Xử lý nhận dạng ký tự cục bộ trực tiếp trên trình duyệt web, không gửi ảnh qua mạng.
- **AI Vision (Tùy chọn nâng cao):**
  - Chỉ kích hoạt khi sinh viên tick chọn rõ ràng: *"Tôi đồng ý gửi ảnh này đến AI provider để trích xuất nội dung bài tập."*
  - Ảnh chỉ được đọc tạm thời vào bộ nhớ RAM trong thời gian xử lý request, **không bao giờ ghi xuống đĩa hoặc lưu vào cơ sở dữ liệu**.
  - Không bao giờ log nội dung ảnh hoặc chuỗi base64.
  - Kết quả Vision được tách cấu trúc thành các trường ứng viên (`candidate fields`): `problem_statement`, `student_code`, `compiler_error`.
  - **Bắt buộc người dùng review:** Sinh viên bắt buộc phải xem lại và chỉnh sửa bản nháp trước khi áp dụng vào trình soạn thảo. **Tuyệt đối không tự động nộp bài (auto-submit) lên gia sư.**

---

## 4. Cơ Chế Xóa Toàn Diện Dữ Liệu Cá Nhân (`delete-all-user-data`)

Hệ thống cung cấp một thao tác duy nhất tại `DELETE /api/user-data` để loại bỏ toàn bộ dữ liệu do người dùng sở hữu:

### 4.1. Phạm Vi Xóa Dữ Liệu
Khi người dùng xác nhận xóa toàn bộ dữ liệu cá nhân:
1. **Tin nhắn gia sư (`tutor_messages`):** Xóa toàn bộ tin nhắn thuộc các phiên học của người dùng.
2. **Kiểm toán thành thạo (`student_mastery_audit`):** Xóa toàn bộ lịch sử audit của người dùng.
3. **Lần thử làm bài (`student_attempts`):** Xóa toàn bộ attempts và mã nguồn đã lưu.
4. **Phiên học tập (`learning_sessions`):** Xóa toàn bộ phiên học đa lượt.
5. **Phiên phân tích (`analysis_sessions`):** Xóa toàn bộ lịch sử phân tích và bài nộp đã lưu.
6. **Điểm thành thạo kỹ năng (`student_skill_mastery`):** Reset và xóa toàn bộ điểm số kỹ năng.
7. **Hồ sơ học viên (`student_profiles`):** Xóa hồ sơ học tập và sở thích sư phạm.
8. **Cài đặt consent chung (`consents`):** Xóa các consent như `privacy_settings`, `analysis_submission`, `tutor_submission`.
9. **Dữ liệu phụ trợ/legacy:** Dọn dẹp sạch sẽ các bản ghi hồ sơ cũ nếu có.

### 4.2. Bảo Lưu Consent Riêng Của AI Vision (`Preserve Vision-specific Consent`)
- Thao tác `delete-all-user-data` **chủ động bảo lưu bản ghi consent đặc thù của Vision** (`consent_type in ('vision', 'vision_ocr', 'vision_consent')`).
- *Lý do sư phạm & trải nghiệm:* Việc xóa lịch sử bài tập và hồ sơ học tập không làm mất đi thỏa thuận cấp phép gửi ảnh lên AI provider mà người dùng đã thiết lập riêng, tránh làm phiền người dùng phải cấu hình lại mỗi khi dọn dẹp bài tập cũ. Nếu muốn thu hồi quyền Vision, người dùng có thể bỏ chọn trực tiếp trong giao diện tải ảnh.

### 4.3. Cô Lập Dữ Liệu Tuyệt Đối (Strict User Ownership)
- Mọi thao tác truy vấn, đọc, sửa, xóa đều được ràng buộc chặt chẽ bởi `current_user.id`.
- Người dùng A tuyệt đối không thể xem, sửa hoặc xóa dữ liệu của người dùng B.

---

## 5. Quy Chuẩn Ghi Log An Toàn (Safe Logging)

Backend và Frontend tuân thủ nghiêm ngặt:
- Không log API Key, mật khẩu, JWT token, Bearer token.
- Không log mã nguồn học viên đầy đủ (`student_code`).
- Không log dữ liệu ảnh, file binary hoặc base64.
- Chỉ log siêu dữ liệu kỹ thuật: provider, model, latency, status code, request id, hoặc error type.

---

## 6. Tài Liệu Liên Quan

- [API Documentation](API_DOCUMENTATION.md)
- [OCR and Vision Plan](OCR_AND_VISION_PLAN.md)
- [Testing Guide](TESTING.md)
- [Deployment Guide](DEPLOYMENT.md)

