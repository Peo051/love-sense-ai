# VietCSharpTutor-600 Dataset

**VietCSharpTutor-600** là bộ dữ liệu chuẩn hóa và kiểm thử benchmark (600 mẫu) dành cho nghiên cứu Gia sư AI lập trình hướng đối tượng C# bằng tiếng Việt cho người mới bắt đầu.

---

## 1. Cấu Trúc Thư Mục
```text
data/vietcsharptutor/
├── README.md                  # Tài liệu giới thiệu bộ dữ liệu
├── schema.json                # JSON Schema 25 thuộc tính chuẩn mực
├── examples.jsonl             # Tập mẫu minh họa đại diện
├── vietcsharptutor_600.jsonl  # Toàn bộ 600 ca benchmark hoàn chỉnh
└── benchmark_report.md        # Báo cáo kiểm định toàn vẹn, phân bố và rò rỉ ranh giới
```

---

## 2. Phân Bố Chủ Đề (10 Nhóm x 60 Mẫu = 600 Mẫu)
1. `class_object`: Khái niệm lớp, đối tượng, khởi tạo thực thể bằng `new` (60 mẫu).
2. `field_property`: Biến trường, thuộc tính đóng gói và auto-property (60 mẫu).
3. `getter_setter`: Khối mã get/set, logic backing field, chống đệ quy vô tận (60 mẫu).
4. `constructor_this`: Hàm khởi tạo mặc định/có tham số, từ khóa `this` chống che khuất (60 mẫu).
5. `method_parameter`: Phương thức thành viên, tham số truyền vào, giá trị trả về (60 mẫu).
6. `encapsulation_validation`: Kiểm tra tính hợp lệ dữ liệu, bảo vệ trạng thái an toàn (60 mẫu).
7. `static_instance`: Thành viên tĩnh (static) vs thành viên thực thể (instance) (60 mẫu).
8. `inheritance_polymorphism`: Kế thừa, từ khóa `base`, `virtual`, `override`, tính đa hình (60 mẫu).
9. `correct_code`: Nhóm đối chứng mã nguồn đúng chuẩn OOP (`no_bug`) (60 mẫu).
10. `insufficient_context`: Nhóm đối chứng mã nguồn dở dang, quá ngắn (`insufficient_context`) (60 mẫu).

---

## 3. Phân Bổ Họ Bài Toán & Tập Dữ Liệu (Zero-Leakage Split)
Bộ dữ liệu được phân chia theo **60 họ bài toán độc lập** (`problem_family_id`):
- **`dev` (Train):** 36 họ bài toán = 360 mẫu (60%).
- **`validation`:** 12 họ bài toán = 120 mẫu (20%).
- **`test` (Đóng băng):** 12 họ bài toán = 120 mẫu (20%).

*Bảo đảm $0\%$ rò rỉ họ bài toán giữa các tập dữ liệu.*

---

## 4. Kiểm Định Bằng Công Cụ Dòng Lệnh
Sử dụng script xác thực để kiểm tra tính hợp lệ của bộ dữ liệu:
```powershell
python scripts/validate_vietcsharptutor.py --data data/vietcsharptutor/vietcsharptutor_600.jsonl --schema data/vietcsharptutor/schema.json
```

---

## 5. Tài Liệu Chi Tiết
Xem toàn bộ quy tắc gán nhãn, chính sách gợi ý và quy trình bình duyệt tại:
- [DATASET_PROTOCOL.md](../../docs/research/DATASET_PROTOCOL.md)
