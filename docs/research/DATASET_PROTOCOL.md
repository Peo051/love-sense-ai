# Giao Thức Khoa Học Bộ Dữ Liệu VietCSharpTutor-600 (Dataset Protocol)

> [!CAUTION]
> **CẢNH BÁO TÍNH TOÀN VẸN NGHIÊN CỨU (RESEARCH INTEGRITY WARNING):**  
> Các số liệu thực nghiệm, chỉ số hiệu năng và kết luận đánh giá trong tài liệu này thuộc bản phát hành lịch sử `codesense-research-v1.0` và **ĐÃ BỊ HỦY BỎ HIỆU LỰC HOÀN TOÀN (INVALIDATED)** theo kết luận kiểm toán độc lập [APT-047](../docs/audit/APT047_EVALUATION_INTEGRITY_VERDICT.md) (commit `4b07ec2`).  
> - Bảng phân loại hiệu lực chi tiết xem tại: [V1_RESULT_STATUS.md](V1_RESULT_STATUS.md).  
> - Bộ dữ liệu `VietCSharpTutor-600` chỉ được coi là: **INTERNAL REGRESSION BENCHMARK ONLY** (Không phải benchmark được ngoại kiểm).  
> - Các hiện vật thực nghiệm lịch sử được lưu trữ nguyên trạng nhằm phục vụ mục đích kiểm toán đối soát minh bạch.

---


**Bộ dữ liệu:** VietCSharpTutor-600  
**Phiên bản:** v1.0.0 (Frozen Test Split)  
**Lĩnh vực:** Trí tuệ nhân tạo trong Giáo dục (AIED), Gia sư lập trình thông minh (Intelligent Tutoring Systems)  
**Ngôn ngữ giải thích:** Tiếng Việt (`vi`)  
**Ngôn ngữ lập trình:** C# (Lập trình hướng đối tượng nhập môn - Beginner OOP)  

---

## 1. Giới Thiệu & Mục Tiêu Nghiên Cứu
VietCSharpTutor-600 là bộ dữ liệu benchmark chuẩn hóa đầu tiên bằng tiếng Việt dành riêng cho việc đánh giá năng lực chẩn đoán lỗi sư phạm và hướng dẫn học tập lập trình C# OOP. Bộ dữ liệu được thiết kế nhằm giải quyết khoảng trống nghiên cứu khi các mô hình ngôn ngữ lớn (LLM) hiện nay có xu hướng cung cấp trực tiếp mã giải hoàn chỉnh (solution dump) thay vì áp dụng phương pháp gợi mở Socratic và gợi ý từng bước (progressive hinting).

---

## 2. Đặc Tả Cấu Trúc Dữ Liệu (25 Thuộc Tính Chuẩn Hóa)

Mỗi mẫu dữ liệu trong VietCSharpTutor-600 là một đối tượng JSON độc lập chứa đầy đủ 25 trường bắt buộc theo [schema.json](../../data/vietcsharptutor/schema.json):

1. `id` (`string`): Định danh duy nhất theo định dạng `vct-[0-9]{3,4}` (ví dụ: `vct-001`).
2. `language` (`string`): Ngôn ngữ tự nhiên sư phạm, cố định là `"vi"`.
3. `topic` (`string`): Chủ đề OOP thuộc 10 phân nhóm (xem Mục 4).
4. `difficulty` (`string`): Mức độ khó sư phạm (`"beginner"`, `"easy"`, `"medium"`).
5. `problem_family_id` (`string`): Mã họ bài toán (ví dụ: `fam-bank-account`) để phân chia split chống rò rỉ ranh giới.
6. `problem_statement_vi` (`string`): Đề bài bài tập lập trình bằng tiếng Việt rõ ràng, chặt chẽ.
7. `student_code` (`string`): Đoạn mã C# nộp lên của học viên (có lỗi, chuẩn xác hoặc dở dang).
8. `compiler_error` (`string | null`): Thông báo lỗi Roslyn C# tương ứng (nếu có) hoặc `null`.
9. `expected_behavior` (`string`): Mô tả hành vi đúng và kết quả cần đạt theo đặc tả bài toán.
10. `bug_status` (`string`): Trạng thái lỗi (`"has_bug"`, `"no_bug"`, `"insufficient_context"`).
11. `error_category` (`string`): Phân loại lỗi chuẩn hóa:
    - `compile_error`: Lỗi cú pháp, thiếu member, sai kiểu dữ liệu.
    - `runtime_error`: Lỗi thực thi (ví dụ: đệ quy vô tận trong getter/setter, NullReference).
    - `logic_error`: Sai logic xử lý, cập nhật trạng thái không đúng, điều kiện sai.
    - `conceptual_misuse`: Dùng sai khái niệm OOP (lạm dụng static, vi phạm đóng gói, nhầm lẫn field/property).
    - `requirement_violation`: Vi phạm đặc tả yêu cầu của bài toán (sai tên class, sai access modifier).
    - `no_bug`: Mã nguồn hoàn toàn chính xác.
    - `insufficient_context`: Mã nguồn quá ngắn hoặc dở dang, chưa đủ thông tin để kết luận.
12. `bug_type` (`string`): Mã lỗi kỹ thuật cụ thể (ví dụ: `encapsulation_break`, `recursive_property`, `static_instance_conflict`, `missing_base_call`).
13. `bug_location` (`string | null`): Vị trí dòng hoặc đoạn mã gây lỗi (hoặc `null` khi `no_bug`/`insufficient_context`).
14. `knowledge_components` (`list[string]`): Danh sách các mã kỹ năng OOP tương ứng trong Skill Taxonomy (ví dụ: `["csharp.encapsulation", "csharp.field"]`).
15. `possible_misconception` (`string | null`): Giả thuyết về ngộ nhận tư duy lập trình của học viên (hoặc `null` khi `no_bug`/`insufficient_context`).
16. `reference_diagnosis` (`string`): Chẩn đoán tham chiếu chuẩn mực từ chuyên gia sư phạm.
17. `evidence` (`string | null`): Trích đoạn bằng chứng từ `student_code` chứng minh chẩn đoán (hoặc `null` khi `no_bug`).
18. `hint_1` (`string`): Gợi ý cấp 1 - Câu hỏi Socratic gợi mở tư duy tổng quan.
19. `hint_2` (`string`): Gợi ý cấp 2 - Giải thích nguyên lý / khái niệm OOP trọng tâm.
20. `hint_3` (`string`): Gợi ý cấp 3 - Hướng dẫn định hướng từng bước hành động (directed hint).
21. `reference_solution` (`string`): Mã nguồn C# chuẩn xác sửa lỗi hoặc mã bài giải tham chiếu.
22. `explanation_vi` (`string`): Lời giải thích sư phạm toàn diện bằng tiếng Việt.
23. `source_type` (`string`): Nguồn tạo mẫu (`"expert_authored"`, `"controlled_mutation"`, `"classroom_observation"`).
24. `split` (`string`): Phân bổ tập dữ liệu (`"dev"`, `"validation"`, `"test"`).
25. `review_status` (`string`): Trạng thái thẩm định (`"draft"`, `"reviewed"`, `"approved"`).

---

## 3. Quy Tắc Gán Nhãn Sư Phạm (Annotation Rules)

### 3.1. Bằng Chứng Mã Nguồn Khách Quan (Evidence Grounding)
- Chẩn đoán lỗi phải căn cứ trực tiếp trên mã nguồn của sinh viên (`student_code`).
- Trường `evidence` phải chứa đoạn trích dẫn thực tế tồn tại trong `student_code`. Tuyệt đối cấm gán nhãn suy diễn không có bằng chứng trong code.

### 3.2. Giả Thuyết Ngộ Nhận (Possible Misconception Semantics)
- Ngộ nhận được định nghĩa dưới dạng giả thuyết sư phạm có thể có của người mới bắt đầu (ví dụ: *"Học viên nhầm tưởng rằng khai báo field public là đủ để các lớp khác sử dụng mà không cần property"*).
- Không phán xét năng lực người học; luôn sử dụng giọng văn khách quan, tôn trọng và mang tính xây dựng.

---

## 4. Quy Chuẩn 3 Cấp Độ Gợi Ý (Hint-Level Rules)

Nhằm ngăn chặn hiện tượng làm lộ lời giải sớm (solution leakage), 3 mức gợi ý tuân thủ chặt chẽ các nguyên tắc sau:

| Cấp Độ Gợi Ý | Mục Tiêu Sư Phạm | Ràng Buộc Kỹ Thuật Nghiêm Ngặt |
| :--- | :--- | :--- |
| **Hint 1: Socratic Question** | Kích hoạt tư duy tự phản biện của học viên. | - Bắt buộc kết thúc bằng câu hỏi gợi mở (`?`).<br>- **Tuyệt đối CẤM trích dẫn code sửa lỗi**.<br>- Không nêu trực tiếp tên giải pháp hoặc thuộc tính cần thêm. |
| **Hint 2: Conceptual Explanation** | Củng cố nguyên lý OOP nền tảng liên quan đến vấn đề. | - Giải thích cơ chế (ví dụ: nguyên lý đóng gói, từ khóa `this`, cơ chế getter/setter).<br>- Được phép đưa ra ví dụ tương tự trừu tượng nhưng **KHÔNG đưa code sửa của bài tập hiện tại**. |
| **Hint 3: Directed Hint** | Hướng dẫn hành động định hướng từng bước. | - Nêu các bước cần làm (ví dụ: *"Bước 1: Chuyển field balance thành private. Bước 2: Tạo property Balance với get và set..."*).<br>- **Không sao chép nguyên vẹn `reference_solution`**. |

---

## 5. Quy Chuẩn Ca Đặc Biệt (Control Groups)

### 5.1. Ca Mã Nguồn Chuẩn Xác (Correct-Code Controls / `no_bug`)
- Khi mã nguồn sinh viên đã đáp ứng đúng và đủ yêu cầu:
  - `bug_status` = `"no_bug"`.
  - `error_category` = `"no_bug"`.
  - `bug_type` = `"no_bug"`.
  - `bug_location` = `null`.
  - `evidence` = `null`.
  - `possible_misconception` = `null`.
  - `hint_1`, `hint_2`, `hint_3`: Đóng vai trò lời khen ngợi, giải thích tại sao code đã chuẩn OOP và gợi ý thử thách nâng cao.

### 5.2. Ca Thiếu Ngữ Cảnh / Mã Dở Dang (Insufficient-Context Controls)
- Khi sinh viên chỉ nộp vài dòng code chưa hoàn chỉnh, thiếu class hoặc thiếu logic chính:
  - `bug_status` = `"insufficient_context"`.
  - `error_category` = `"insufficient_context"`.
  - `bug_type` = `"code_too_brief"`.
  - `possible_misconception` = `null`.
  - `hint_1`, `hint_2`, `hint_3`: Hướng dẫn sinh viên hoàn thiện thêm thân phương thức, khai báo lớp và cung cấp đủ ngữ cảnh bài tập.

---

## 6. Phân Bổ Họ Bài Toán & Chống Rò Rỉ Dữ Liệu (Family-Level Splitting)

- **Nguyên lý cốt lõi:** Ngăn chặn tuyệt đối việc LLM "học vẹt" đề bài từ tập huấn luyện rồi dự đoán đúng trên tập kiểm tra (data leakage).
- **Quy tắc:**
  - Toàn bộ 600 ca dữ liệu được cấu trúc từ **60 họ bài toán độc lập** (`problem_family_id`).
  - Mọi biến thể mang cùng một `problem_family_id` **bắt buộc phải nằm trong cùng một `split`**.
  - **Tỷ lệ phân bổ:**
    - `dev`: 36 họ bài toán = 360 mẫu (60%).
    - `validation`: 12 họ bài toán = 120 mẫu (20%).
    - `test`: 12 họ bài toán = 120 mẫu (20%).
  - **Kiểm toán rò rỉ ranh giới:** Tập giao $	ext{Families}(	ext{dev}) \cap 	ext{Families}(	ext{validation}) \cap 	ext{Families}(	ext{test}) = \emptyset$ ($0\%$ leakage).
- **Đóng băng tập Test (Test Split Freeze):**
  - Tập `test` được tính toán mã băm SHA-256 cố định và đóng băng trước khi thực hiện bất kỳ thử nghiệm tối ưu prompt hay huấn luyện mô hình nào.

---

## 7. Quy Tắc Chống Trùng Lặp (Duplicate Rules)
- Mỗi mẫu có mã `id` duy nhất trên toàn bộ dataset.
- Tuyệt đối cấm trùng lặp hoàn toàn cặp `(problem_statement_vi, student_code)`.
- Không tạo các biến thể hời hợt chỉ thay đổi tên biến (ví dụ: `x -> y`) mà không thay đổi cấu trúc lỗi hoặc kịch bản sư phạm.

---

## 8. Quy Trình Thẩm Định 2 Cấp (Review Process)
1. **Cấp 1 - Authoring & Draft (`draft`):** Tác giả biên soạn mẫu dữ liệu, chạy kiểm tra cú pháp và schema tự động.
2. **Cấp 2 - Peer Review (`reviewed`):** Giảng viên / Chuyên gia kiểm định độc lập kiểm tra:
   - Tính chính xác của chẩn đoán kỹ thuật và lỗi Roslyn C#.
   - Tính sư phạm của 3 cấp độ gợi ý (đặc biệt kiểm tra có lộ code sửa không).
   - Ngữ pháp tiếng Việt và thuật ngữ OOP chuẩn mực.
3. **Cấp 3 - Dataset Approval (`approved`):** Chủ nhiệm bộ dữ liệu phê duyệt đưa mẫu vào benchmark chính thức.

---

## 9. Chính Sách Bảo Mật & Quyền Riêng Tư (Privacy Rules)
- Bộ dữ liệu tuân thủ nghiêm ngặt nguyên tắc **Không thu thập và không chứa thông tin định danh cá nhân (No PII)**:
  - Không chứa tên sinh viên, mã số sinh viên, tên trường học, email hoặc đường dẫn nội bộ.
  - Tên định danh trong các bài toán là các thực thể hư cấu kinh điển (ví dụ: `TaiKhoanNganHang`, `HocSinh`, `NhanVien`, `HinhHoc`).
  - Không sao chép nguyên văn các bài nộp riêng tư chưa có sự đồng ý của sinh viên.
