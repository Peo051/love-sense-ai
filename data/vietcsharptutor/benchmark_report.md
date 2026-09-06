# Báo Cáo Kiểm Định Bộ Dữ Liệu VietCSharpTutor-600 (Benchmark Report)

- **Thời điểm kiểm định:** `Tự động tạo`
- **Tổng số mẫu:** `600` (Yêu cầu: 600)
- **Số họ bài toán độc lập (`problem_family_id`):** `60` (Yêu cầu: 60)
- **Tình trạng rò rỉ họ bài toán (Family Leakage):** `KHÔNG (Zero Leakage)`
- **Mã băm toàn vẹn (SHA-256):** `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed`
- **Trạng thái đóng băng tập Test:** `ĐÃ ĐÓNG BĂNG (FROZEN)`

---

## 1. Phân Bổ Theo Split
| Split | Số Lượng Mẫu | Tỷ Lệ (%) | Yêu Cầu Mục Tiêu |
| :--- | :--- | :--- | :--- |
| `dev` | 360 | 60.0% | 360 |
| `validation` | 120 | 20.0% | 120 |
| `test` | 120 | 20.0% | 120 |

---

## 2. Phân Bổ Theo 10 Chủ Đề OOP
| Chủ Đề (`topic`) | Số Lượng Mẫu | Mục Tiêu Chuẩn | Trạng Thái |
| :--- | :--- | :--- | :--- |
| `class_object` | 60 | 60 | ĐẠT (60) |
| `constructor_this` | 60 | 60 | ĐẠT (60) |
| `correct_code` | 60 | 60 | ĐẠT (60) |
| `encapsulation_validation` | 60 | 60 | ĐẠT (60) |
| `field_property` | 60 | 60 | ĐẠT (60) |
| `getter_setter` | 60 | 60 | ĐẠT (60) |
| `inheritance_polymorphism` | 60 | 60 | ĐẠT (60) |
| `insufficient_context` | 60 | 60 | ĐẠT (60) |
| `method_parameter` | 60 | 60 | ĐẠT (60) |
| `static_instance` | 60 | 60 | ĐẠT (60) |

---

## 3. Phân Bổ Phân Nhóm Lỗi (Error Category)
| Phân Loại (`error_category`) | Số Lượng |
| :--- | :--- |
| `compile_error` | 240 |
| `logic_error` | 120 |
| `runtime_error` | 60 |
| `conceptual_misuse` | 60 |
| `no_bug` | 60 |
| `insufficient_context` | 60 |

---

## 4. Báo Cáo Kiểm Tra Trùng Lặp & Rò Rỉ Ranh Giới
- **Trùng lặp ID:** `0`
- **Trùng lặp nội dung đề bài + code:** `0`
- **Số họ bài toán bị rò rỉ split:** `0` (Yêu cầu = 0)
- **Kết luận thẩm định:** `HỢP LỆ VÀ SẴN SÀNG CHO BENCHMARK THỰC NGHIỆM`
