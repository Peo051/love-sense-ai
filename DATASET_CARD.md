# Thẻ Dữ Liệu: VietCSharpTutor-600 (Dataset Card)

- **Tên bộ dữ liệu:** `VietCSharpTutor-600`
- **Phiên bản:** `v1.0.0`
- **Ngôn ngữ tự nhiên:** Tiếng Việt (`vi`)
- **Ngôn ngữ lập trình:** C# / .NET 8 (Nhập môn Lập trình Hướng đối tượng - Beginner OOP)
- **Kích thước:** Đúng 600 mẫu dữ liệu chuẩn hóa
- **Số họ bài toán (`problem_family_id`):** 60 họ bài toán độc lập
- **Giấy phép phát hành:** MIT License / Research Open Access
- **Tập tin chính:** `data/vietcsharptutor/vietcsharptutor_600.jsonl`
- **Tập tin mẫu ví dụ:** `data/vietcsharptutor/examples.jsonl`
- **Lược đồ kiểm định:** `data/vietcsharptutor/schema.json`

---

## 1. Mục Đích & Bối Cảnh (Dataset Purpose & Motivation)

Bộ dữ liệu **VietCSharpTutor-600** được xây dựng nhằm cung cấp một thước đo benchmark khách quan, độc lập và chuẩn mực để đánh giá năng lực sư phạm của các hệ thống gia sư lập trình thông minh (Intelligent Tutoring Systems) và các mô hình ngôn ngữ lớn (LLMs).

Khác biệt với các tập dữ liệu lập trình thông thường vốn chỉ tập trung vào việc tạo mã (Code Generation) hoặc sửa lỗi tự động (Automated Program Repair), VietCSharpTutor-600 đặt trọng tâm vào **Năng lực Sư phạm và Dàn dựng Nhận thức (Pedagogical Scaffolding)**:
- Không chỉ đánh giá việc tìm ra lỗi, mà đánh giá khả năng giải thích nguồn gốc lỗi và quan niệm sai lầm (Misconceptions).
- Đánh giá khả năng cung cấp 3 tầng gợi ý tăng dần (Progressive Hints) mà **không làm lộ mã nguồn giải pháp (Zero Solution Leakage)**.
- Bao gồm các ca đối chứng quan trọng: mã nguồn hoàn toàn đúng (`correct_code` / `no_bug`) và mã nguồn bị cắt đoạn thiếu ngữ cảnh (`insufficient_context`).

---

## 2. Phân Bổ Dữ Liệu (Dataset Distribution)

### 2.1. Phân bổ theo 10 Chủ đề OOP (10 Topics $\times$ 60 mẫu = 600 mẫu)
1. `class_object` (60 ca): Khai báo lớp, khởi tạo đối tượng, cấp phát bộ nhớ heap, lỗi biến tham chiếu null.
2. `field_property` (60 ca): Phân biệt trường dữ liệu (fields) và thuộc tính (properties), access modifiers (`private`, `public`).
3. `getter_setter` (60 ca): Thuộc tính tự động vs explicit getter/setter kèm biến sao lưu backing field, lỗi đệ quy vô hạn.
4. `constructor_this` (60 ca): Hàm tạo khởi tạo dữ liệu, phân biệt tầm vực giữa tham số và trường qua từ khóa `this`.
5. `method_parameter` (60 ca): Chữ ký phương thức, kiểu trả về (`void` vs giá trị), truyền tham số.
6. `encapsulation_validation` (60 ca): Tính đóng gói, bảo vệ quy tắc bất biến (invariants), kiểm tra điều kiện dữ liệu trong setter/method.
7. `static_instance` (60 ca): Phân biệt thành viên tĩnh (`static`) và thành viên thực thể (`instance`), ngữ cảnh gọi trong `Main`.
8. `inheritance_polymorphism` (60 ca): Kế thừa lớp cha - con, liên kết động đa hình, cặp từ khóa `virtual` / `override`.
9. `correct_code` (60 ca - Nhóm đối chứng): Mã nguồn chuẩn mực, không có lỗi cú pháp hay logic, kiểm tra tỷ lệ báo lỗi oan (False Positive Rate).
10. `insufficient_context` (60 ca - Nhóm đối chứng): Đoạn mã bị khuyết ngữ cảnh, thiếu định nghĩa lớp hoặc kiểu phụ thuộc.

### 2.2. Phân bổ Split Độc Lập Theo Họ Bài Toán (Zero Family Leakage)
Để ngăn chặn hoàn toàn hiện tượng học vẹt hoặc rò rỉ dữ liệu (Data Leakage) giữa các tập, việc phân chia split được thực hiện nghiêm ngặt ở cấp độ họ bài toán (`problem_family_id`):
- **Tập Phát Triển (`dev`):** 36 họ bài toán ($36 \times 10 = 360$ mẫu, chiếm 60%).
- **Tập Thẩm Định (`validation`):** 12 họ bài toán ($12 \times 10 = 120$ mẫu, chiếm 20%).
- **Tập Kiểm Thử Đóng Băng (`test`):** 12 họ bài toán ($12 \times 10 = 120$ mẫu, chiếm 20%).
- **Tỷ lệ rò rỉ họ bài toán:** **0.0% (Zero Leakage)**.

---

## 3. Cấu Trúc Bản Ghi (Schema Specification)

Mỗi mẫu dữ liệu trong file JSONL bao gồm đúng **25 trường bắt buộc**:

| STT | Tên Trường | Kiểu Dữ Liệu | Ý Nghĩa Sư Phạm |
| :--- | :--- | :--- | :--- |
| 1 | `id` | string | Định danh duy nhất theo định dạng `^vct-[0-9]{3,4}$`. |
| 2 | `language` | string | Ngôn ngữ tự nhiên sư phạm (`vi`). |
| 3 | `topic` | string | Một trong 10 chủ đề OOP. |
| 4 | `difficulty` | string | `beginner`, `easy`, hoặc `medium`. |
| 5 | `problem_family_id` | string | Mã họ bài toán (ví dụ: `fam-student-profile`). |
| 6 | `problem_statement_vi`| string | Đề bài lập trình bằng tiếng Việt. |
| 7 | `student_code` | string | Đoạn mã nguồn học viên nộp. |
| 8 | `compiler_error` | string / null| Thông báo lỗi Roslyn C# (nếu có). |
| 9 | `expected_behavior` | string | Hành vi và kết quả mong đợi. |
| 10 | `bug_status` | string | `has_bug`, `no_bug`, hoặc `insufficient_context`. |
| 11 | `error_category` | string | Phân loại kỹ thuật (`compile_error`, `runtime_error`, `logic_error`, v.v.). |
| 12 | `bug_type` | string | Định danh cụ thể dạng lỗi. |
| 13 | `bug_location` | object / null| Vị trí `{file, start_line, end_line, symbol}`. |
| 14 | `knowledge_components`| array | Danh sách thẻ kiến thức OOP (KCs). |
| 15 | `possible_misconception`| string / null| Mô hình quan niệm sai lầm cốt lõi của sinh viên. |
| 16 | `reference_diagnosis` | string | Chẩn đoán chuẩn mực của chuyên gia. |
| 17 | `evidence` | string / null| Chuỗi con nguyên văn (exact substring) trong student_code. |
| 18 | `hint_1` | string | Gợi ý bậc 1: Định hướng tư duy (không có code). |
| 19 | `hint_2` | string | Gợi ý bậc 2: Giải thích khái niệm OOP nền tảng. |
| 20 | `hint_3` | string | Gợi ý bậc 3: Hướng dẫn hành động sửa lỗi. |
| 21 | `reference_solution` | string | Mã giải pháp C# chuẩn mực. |
| 22 | `explanation_vi` | string | Giải thích sư phạm chi tiết cho người mới học. |
| 23 | `source_type` | string | `expert_authored`, `controlled_mutation`, v.v. |
| 24 | `split` | string | `dev`, `validation`, hoặc `test`. |
| 25 | `review_status` | string | Trạng thái thẩm định (`approved`). |

---

## 4. Kiểm Định Chất Lượng & Quy Chuẩn Đạo Đức (Quality & Ethics)

1. **Bảo vệ quyền riêng tư sinh viên:** Bộ dữ liệu không sao chép nguyên văn bài tập hay thông tin nhạy cảm của bất kỳ sinh viên thực tế nào. Tất cả các ca lỗi được tổng hợp từ quan sát thực tế trong giảng dạy đại học và đột biến kiểm soát (controlled mutation).
2. **Không trùng lặp:** Kiểm định băm SHA-256 xác nhận 0 ca trùng lặp nội dung đề bài + mã nguồn.
3. **Neo bằng chứng 100%:** Toàn bộ bằng chứng `evidence` của các ca lỗi bắt buộc phải tồn tại nguyên văn trong `student_code`.
4. **Không tái phân phối dữ liệu bên ngoài trái phép:** Bộ dữ liệu là sản phẩm nghiên cứu độc lập của dự án CodeSense AI, không phụ thuộc hay vi phạm bản quyền dữ liệu của bên thứ ba.
