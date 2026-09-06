# Lộ Trình Phát Triển Hệ Thống (Project Roadmap)

Lộ trình phát triển và các cột mốc kỹ thuật - nghiên cứu của dự án **CodeSense AI - Adaptive Programming Tutor**.

---

## 1. Lịch Sử Chuyển Đổi & Cột Mốc Đã Hoàn Thành (`implemented`)

### Phiên Bản v1.0.0 — Nền Tảng Gia Sư Lập Trình Thích Ứng & Nghiên Cứu Benchmark (Hiện Tại)
- **Kiến trúc & Hạ tầng Cốt lõi (APT-001 đến APT-015):**
  - Chuyển hướng thành công dự án sang Intelligent Tutoring System (ITS) cho C# OOP.
  - Xây dựng 18 endpoints RESTful trên FastAPI và PostgreSQL.
  - Tích hợp xác thực phân quyền qua Firebase Admin SDK.
  - Phát triển giao diện người dùng Next.js 16 App Router responsive (Tutor, Progress, History, OCR).
- **Mô hình Hóa Người Học & Sư Phạm Tăng Dần (APT-016 đến APT-025):**
  - Hiện thực hóa cơ chế Progressive Scaffolding 3 bậc (Directional -> Conceptual -> Tactical).
  - Tích hợp Knowledge Tracing theo dõi độ thuần thục của 10+ KCs.
  - Xây dựng cơ chế kiểm soát quyền riêng tư hai lớp (`save_result` phân tách `save_input`) và Right to Erasure.
- **Nghiên Cứu Khoa Học & Đánh Giá Đóng Băng (APT-026 đến APT-035):**
  - Xây dựng và thẩm định chuẩn mực bộ dữ liệu **VietCSharpTutor-600** (60 families, 10 topics, 0% leakage).
  - Phát triển bộ công cụ Evaluation Runner cho 4 hệ thống (Baseline A, B, Proposed C, D).
  - Triển khai bộ tính toán 11 chỉ số sư phạm độc lập và 5 cấu hình nghiên cứu triệt tiêu (Ablation).
  - Thực thi Frozen Experimental Protocol với kiểm định thống kê McNemar ($p < 0.001$) và Bootstrap 95% CI.
  - Kiểm định toàn diện 18 flows và 7 security checks đạt 100% PASS.

---

## 2. Các Kế Hoạch Đang Triển Khai (`planned`) — Dự Kiến v1.2

- **Hỗ trợ Đa Ngôn ngữ OOP (Multi-Language OOP Support):**
  - Mở rộng bộ phân tích cú pháp và quy tắc sư phạm sang Java OOP và Python OOP.
  - Xây dựng tập dữ liệu đối sánh `VietJavaTutor` và `VietPythonTutor`.
- **Tiện Ích Mở Rộng IDE (VS Code Extension):**
  - Đưa trực tiếp CodeSense AI vào môi trường Visual Studio Code của sinh viên.
  - Hỗ trợ chẩn đoán tại chỗ khi gặp lỗi biên dịch Roslyn ngay trong trình soạn thảo.
- **Bộ Sinh Bài Tập Tự Động Thích Ứng (Adaptive Problem Generator):**
  - Tự động sinh các biến thể bài tập mới tập trung vào các KCs mà sinh viên còn yếu (Mastery < 0.7).

---

## 3. Các Tính Năng Thực Nghiệm (`experimental`) — Dự Kiến v1.5

- **Nhận Diện Tải Nhận Thức (Cognitive Load & Hesitation Detection):**
  - Phân tích độ trễ giữa các lần sửa mã, thời gian dừng gõ và tần suất xóa code để ước lượng mức độ bối rối của người học.
  - Tự động hạ độ phức tạp của gợi ý khi phát hiện người học rơi vào trạng thái bế tắc (frustration).
- **Phân Tích Cảm Xúc Sư Phạm Trong Hỏi Đáp Tự Do (Pedagogical Affect Analysis):**
  - Nhận diện thái độ tích cực, tự tin hoặc thất vọng trong câu hỏi tự do của học viên nhằm phản hồi ân cần, khích lệ.

---

## 4. Tầm Nhìn Dài Hạn (`future work`) — Dự Kiến v2.0

- **Bảng Điều Khiển Giảng Viên & Quản Lý Lớp Học (Instructor Classroom Analytics):**
  - Bảng tổng hợp real-time cho giảng viên biết chủ đề OOP nào cả lớp đang gặp nhiều quan niệm sai lầm nhất.
  - Phân cụm học sinh theo mức độ tiến bộ để hỗ trợ phụ đạo kịp thời.
- **Container Cát Lún Tự Động Chấm Điểm (Sandboxed Dynamic Test Execution):**
  - Triển khai micro-containers bảo mật (gVisor/Firecracker) để chạy test case động trên mã nguồn sinh viên mà không ảnh hưởng an ninh máy chủ.
