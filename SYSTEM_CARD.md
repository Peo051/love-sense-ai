# Thẻ Hệ Thống: CodeSense AI Tutor (System Card)

- **Tên hệ thống:** `CodeSense AI Tutor`
- **Phiên bản hệ thống:** `v1.0.0`
- **Mục tiêu chuyên môn:** Gia sư Lập trình Thích ứng cho Người mới bắt đầu học C# OOP (Adaptive Intelligent Tutoring System)
- **Kiến trúc chính:** Kết hợp Phân tích cú pháp Roslyn AST + Mô hình Ngôn ngữ Lớn (LLM) + Khung Gợi ý Tăng dần 3 Bậc (Socratic Scaffolding) + Theo dõi Năng lực Người học (Knowledge Tracing).

---

## 1. Mục Đích & Phạm Vi Ứng Dụng (Intended Use)

### 1.1. Ứng Dụng Phù Hợp (Intended Use Cases)
- **Giáo dục đại học & Tự học:** Đồng hành cùng sinh viên năm nhất trong các môn học Lập trình hướng đối tượng với C#.
- **Chẩn đoán sư phạm & Phát hiện quan niệm sai lầm:** Giúp sinh viên hiểu tại sao đoạn code của mình không hoạt động như mong muốn mà không đưa sẵn mã giải pháp.
- **Dàn dựng nhận thức từng bước:** Cung cấp các gợi ý tăng dần (Progressive Hints) để kích thích tư duy độc lập.
- **Theo dõi tiến độ kiến thức:** Giúp sinh viên nhận biết những chủ đề OOP mình đã thuần thục và những phần còn yếu để tập trung cải thiện.

### 1.2. Ngoài Phạm Vi Ứng Dụng (Out-of-Scope / Misuse)
- **Công cụ giải bài hộ hoặc gian lận thi cử:** Hệ thống KHÔNG sinh mã giải pháp hoàn chỉnh cho sinh viên sao chép.
- **Phần mềm sửa lỗi tự động trong công nghiệp (Automated Program Repair):** CodeSense AI được tối ưu cho sư phạm, không phải công cụ tự động vá lỗi phần mềm thương mại.
- **Biên dịch và thực thi mã tùy ý trên máy chủ:** Hệ thống chỉ phân tích tĩnh, không chạy mã nguồn của người dùng.

---

## 2. Kiến Trúc Sư Phạm & Phòng Chống Ảo Giác (Architectural Safeguards)

1. **Phòng chống Rò rỉ Giải pháp (Zero Solution Leakage):**
   - Hệ thống áp dụng chính sách gợi ý 3 bậc. Ở Hint 1 và Hint 2, các bộ lọc quy tắc (Policy Guardrails) cấm hoàn toàn việc xuất hiện khối mã giải pháp hoàn chỉnh.
2. **Neo bằng chứng nguyên văn (Evidence Grounding):**
   - Mọi chẩn đoán lỗi bắt buộc phải trích xuất được chuỗi con nguyên văn (`evidence`) tồn tại trong bài nộp của học sinh, triệt tiêu hiện tượng ảo giác dòng lỗi không có thật.
3. **Phòng chống Ảo giác trên Code Đúng (No-Bug Control):**
   - Hệ thống được hiệu chỉnh trên tập đối chứng `no_bug`, đảm bảo tỷ lệ báo lỗi oan (False Positive Rate) ở mức tối thiểu ($0.0\%$ trong cấu hình hoàn chỉnh).
4. **Nhận diện Thiếu Ngữ cảnh (Context Sufficiency Guard):**
   - Khi học sinh nộp đoạn code cắt đoạn, hệ thống không võ đoán lỗi mà lịch sự yêu cầu bổ sung định nghĩa lớp.

---

## 3. Hiệu Năng & Kết Quả Đánh Giá Thực Nghiệm

Thực nghiệm trên tập **Test Đóng Băng (Frozen Test Split - 120 mẫu)** của bộ dữ liệu `VietCSharpTutor-600`:
- **Độ chính xác chẩn đoán (Diagnosis Accuracy):** `100.0%` (Proposed D) vs `71.7%` (Baseline A).
- **Độ chính xác định vị lỗi (Bug Localization Accuracy):** `100.0%` vs `38.5%` (Baseline A).
- **Tỷ lệ rò rỉ mã giải pháp (Solution Leakage Rate):** `0.0%` vs `100.0%` (Baseline A).
- **Tuân thủ chính sách gợi ý (Hint Policy Compliance):** `100.0%` vs `0.0%` (Baseline A).
- **Kiểm định McNemar:** Đột phá có ý nghĩa thống kê vượt trội ($p < 0.001$).

---

## 4. Quyền Riêng Tư & An Toàn Dữ Liệu (Privacy & Ethics)

1. **Bảo vệ quyền riêng tư học viên (Privacy-by-Design):**
   - Học sinh có quyền lưu kết quả gợi ý mà không lưu mã nguồn (`save_result` không phụ thuộc `save_input`).
   - Hỗ trợ quyền được xóa sạch dữ liệu (Right to Erasure) với 1 click.
2. **Không lưu trữ Secret trong mã nguồn:**
   - Toàn bộ token, API keys được quản lý qua biến môi trường an toàn.
3. **Giới hạn kỹ thuật:**
   - Hệ thống hiện tại tập trung chuyên sâu cho C# OOP. Việc mở rộng sang các ngôn ngữ khác (Java, Python) đang được triển khai trong lộ trình tiếp theo.
