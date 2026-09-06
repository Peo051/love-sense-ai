# Kịch Bản Trình Chiếu CodeSense AI (3-Phút Demo Script)

Tài liệu hướng dẫn trình diễn nhanh (3 phút) nền tảng **CodeSense AI - Adaptive Programming Tutor**.

---

## Chuẩn Bị Trước Demo
- Mở trang chủ ứng dụng: `http://localhost:3000` (hoặc domain production).
- Backend API server đang chạy: `http://localhost:8000`.
- Tài khoản sinh viên demo sẵn sàng hoặc sử dụng chế độ Khách (Guest Demo).
- Chuẩn bị một đoạn mã C# có lỗi nhập môn điển hình (ví dụ: lỗi gán biến tham số che khuất trường `name = name;` trong hàm tạo).

---

## Kịch Bản 3 Phút (Timeline)

### 0:00 - 0:30: Đặt Vấn Đề & Giới Thiệu CodeSense AI
- **Hành động:** Mở trang chủ (`/tutor`).
- **Nội dung trình bày:**
  - "Khi sinh viên năm nhất học lập trình hướng đối tượng C#, các bạn thường hỏi ChatGPT hoặc Copilot và nhận ngay đoạn code giải pháp hoàn chỉnh."
  - "Điều này khiến sinh viên không hiểu bản chất và mất đi kỹ năng tư duy phản biện."
  - "CodeSense AI giải quyết vấn đề này bằng phương pháp gia sư Socratic: chẩn đoán có cấu trúc, gợi ý tăng dần 3 bậc không làm lộ giải pháp, và đồng hành thích ứng theo năng lực học viên."

### 0:30 - 1:15: Trải Nghiệm Gia Sư Socratic & Chẩn Đoán Cấu Trúc
- **Hành động:** 
  - Dán đoạn mã C# có lỗi:
    ```csharp
    public class Student {
        public string Name;
        public Student(string name) {
            Name = name; // Hoặc gán nhầm name = name;
        }
    }
    ```
  - Nhấn `Phân tích & Gợi ý`.
- **Điểm cần nhấn mạnh:**
  - Hệ thống bóc tách chính xác loại lỗi (`logic_error`), neo đúng vị trí dòng và trích xuất bằng chứng nguyên văn.
  - Sinh viên nhận **Hint 1 (Định hướng)**: Câu hỏi gợi mở tư duy, không hề có dòng code giải pháp nào bị lộ.

### 1:15 - 1:55: Mở Tầng Gợi Ý 2 & Thực Hiện Sửa Lỗi (Verify Fix)
- **Hành động:**
  - Nhấn `Gợi ý tiếp theo` -> Hệ thống mở **Hint 2 (Khái niệm)** giải thích nguyên lý từ khóa `this` và tầm vực biến.
  - Sửa lại code thành `this.Name = name;` và nhấn `Kiểm tra mã sửa (Verify Fix)`.
- **Điểm cần nhấn mạnh:**
  - Hệ thống kiểm định tức thì, chúc mừng sinh viên đã tự khắc phục được lỗi và cập nhật điểm thuần thục (Mastery Score) cho KCs `OOP.Constructors` và `OOP.ThisKeyword`.

### 1:55 - 2:35: Bảng Theo Dõi Năng Lực (Mastery Progress Dashboard)
- **Hành động:** Chuyển sang trang `/progress`.
- **Điểm cần nhấn mạnh:**
  - Bảng trực quan hóa mức độ thuần thục của 10+ Thành phần Kiến thức (KCs).
  - Lịch sử giải bài chi tiết, giúp người học nhận ra điểm mạnh và chủ đề cần cải thiện.

### 2:35 - 3:00: Quyền Riêng Tư & Tổng Kết
- **Hành động:** Mở mục Cài đặt quyền riêng tư (`Privacy Settings`).
- **Điểm cần nhấn mạnh:**
  - Tính năng phân tách: Cho phép lưu kết quả phân tích mà không cần lưu trữ mã nguồn thô của học sinh.
  - Quyền được xóa sạch dữ liệu (Full Purge) chỉ với 1 click theo chuẩn GDPR.
  - Kết luận: CodeSense AI biến AI từ công cụ gian lận/làm hộ thành người thầy đồng hành thông thái.
