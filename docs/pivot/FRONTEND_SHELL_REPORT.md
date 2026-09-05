# CodeSense AI - Frontend Shell Migration Report (APT-003)

Established on: 2026-09-05  
Branch: `adaptive-programming-tutor`  
Task: APT-003 - Remove relationship-specific frontend  

---

## 1. Mục tiêu hoàn thành

Loại bỏ toàn bộ giao diện người dùng, nội dung văn bản, biểu đồ và form liên quan đến phân tích tình cảm/đối phương (partner/romance). Chuẩn bị sẵn khung frontend shell cho hệ thống **Gia sư lập trình thích ứng C# OOP (CodeSense AI)**.

---

## 2. Chi tiết các thay đổi

### 2.1 Cấu trúc điều hướng (Navigation & Routes)
- **Navbar & Footer** (`frontend/components/common/Navbar.tsx`, `Footer.tsx`):
  - Khởi tạo 5 routes hoạt động: `/tutor`, `/progress`, `/history`, `/profile`, `/privacy`.
  - Loại bỏ các đường dẫn `/analyze` cũ khỏi thanh điều hướng chính.
- **Trang chủ** (`frontend/app/page.tsx`, `frontend/components/home/HeroVisual.tsx`):
  - Thay đổi Hero visual từ chat tin nhắn tình cảm sang bản xem trước mã nguồn C# OOP (`BankAccount.cs`), chẩn đoán nguyên lý Encapsulation và gợi ý Socratic.
  - Cập nhật quy trình 3 bước sang: Dán code/Ảnh chụp bài tập -> AI chẩn đoán lỗi OOP & đặt câu hỏi gợi mở -> Theo dõi lộ trình nắm vững OOP.
  - Chuyển hướng các nút CTA chính sang `/tutor`.
- **Đăng nhập & Auth Callback** (`frontend/app/login/page.tsx`, `frontend/app/auth/page.tsx`):
  - Điều hướng mặc định sau đăng nhập thành công là `/tutor`.

### 2.2 Các Routes ứng dụng
1. `/tutor` (`frontend/app/tutor/page.tsx`):
   - Đặt banner cảnh báo nổi bật: **Hệ thống đang nâng cấp backend (Tutor Backend Migration In Progress)**.
   - Hỗ trợ chọn chủ đề C# OOP (Classes, Encapsulation, Inheritance, Polymorphism, Abstraction/Interface, Exception Handling).
   - Ô nhập mô tả bài tập / lỗi compiler và editor nhập mã nguồn C#.
   - Tích hợp tab quét mã nguồn từ ảnh bài tập (OCR) tái sử dụng hạ tầng `ImageOcrUploader`.
   - Cột gợi ý nguyên tắc sư phạm Socratic và ví dụ gợi ý C# OOP.
2. `/progress` (`frontend/app/progress/page.tsx`):
   - Hiển thị lộ trình 5 module C# OOP cơ bản đến nâng cao.
   - Thống kê tiến độ học tập và mức độ độc lập tư duy.
   - Bảo vệ phiên bằng `AuthRequiredState` khi chưa đăng nhập.
3. `/history` (`frontend/app/history/page.tsx`):
   - Chuyển đổi thành "Lịch sử thực hành & bài nộp".
   - Hiển thị bài nộp code, chẩn đoán OOP và căn cứ dòng code.
   - Giữ nguyên các chức năng xóa phiên đơn lẻ và xóa toàn bộ lịch sử.
4. `/profile` (`frontend/app/profile/page.tsx`):
   - Chuyển đổi thành "Hồ sơ học viên" (Biệt danh, Ngôn ngữ lập trình C#, Trình độ hiện tại, Mục tiêu OOP cần cải thiện).
   - **Xóa bỏ 100% UI thẻ "Hồ sơ người ấy" (partner profile)** khỏi tầm nhìn của học viên.
   - Giữ compatibility ngầm với backend API schema (`POST /api/profile` vẫn gửi cấu trúc payload hợp lệ).
5. `/privacy` (`frontend/app/privacy/page.tsx`):
   - Làm sạch toàn bộ thuật ngữ tình cảm, thay bằng "hồ sơ học viên", "mã nguồn bài tập".
   - Giữ nguyên cơ chế bảo vệ quyền riêng tư, kiểm soát lưu trữ consent và cascade deletion (`DELETE /api/user-data`).
6. `/analyze` (`frontend/app/analyze/page.tsx`):
   - Chuyển hướng tự động client-side sang `/tutor`, đảm bảo không còn bất kỳ UI nào hỏi chat tình cảm nếu truy cập URL cũ.

---

## 3. Kết quả kiểm thử & Build

| Bộ kiểm thử / Kiểm tra | Lệnh | Kết quả | Trạng thái |
|---|---|---|---|
| **Frontend Vitest Suites** | `npx vitest run` | 8/8 files passed, 24/24 tests passed | **PASS** |
| **TypeScript Typecheck** | `npm run typecheck` | 0 errors | **PASS** |
| **Next.js Production Build** | `npm run build` | 100% static generation (11/11 pages) | **PASS** |
| **Backend Pytest Suite** | `pytest tests` | 94/94 passed | **PASS** |

---

## 4. Tiêu chí nghiệm thu (Acceptance Criteria)

- [x] Không còn bất kỳ UI đang hoạt động nào hỏi người dùng về tin nhắn tình cảm hay thông tin người yêu (partner).
- [x] Đăng nhập Google / Firebase vẫn hoạt động bình thường.
- [x] Hệ thống quyền riêng tư (Privacy & Consent) hoạt động đầy đủ.
- [x] Hệ thống điều hướng trực quan khớp hoàn toàn với các routes mới (`/tutor`, `/progress`, `/history`, `/profile`, `/privacy`).
