# BÁO CÁO KIỂM TOÁN NGUỒN GỐC DỰ ĐOÁN 30 CA THỰC NGHIỆM (APT-045)

> **Mã kiểm toán**: APT-045  
> **Chức danh kiểm toán**: Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
> **Dự án**: CodeSense AI - Adaptive Programming Tutor  
> **Bộ dữ liệu mục tiêu**: VietCSharpTutor-600 (`data/vietcsharptutor/vietcsharptutor_600.jsonl`)  
> **Phiên bản đóng băng**: `codesense-research-v1.0`  
> **Nhánh kiểm toán**: `audit/evaluation-integrity-v1`  
> **Ngày thực hiện**: 2026-09-06  

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Kiểm toán viên nghiên cứu độc lập đã tiến hành kiểm tra truy vết nguồn gốc (Provenance Audit) cho **đúng 30 ca đánh giá cụ thể**:
- **10 ca tập Dev**: `vct-001` đến `vct-010` (Hệ thống Proposed C)
- **10 ca tập Validation**: `vct-361` đến `vct-370` (Hệ thống Proposed D)
- **10 ca tập Frozen Test**: `vct-481` đến `vct-490` (Hệ thống Proposed D)

> [!IMPORTANT]
> **NGUYÊN TẮC ĐÓNG BĂNG**: Toàn bộ 10 ca tập Test đều được kiểm tra ngoại tuyến (offline inspection) trực tiếp từ tệp kết quả đông băng `runs/run_D_test_20260906_103703/predictions.jsonl`. Tuyệt đối không thực hiện bất kỳ lệnh gọi LLM mới nào.

### Thống kê tổng hợp nguồn gốc (Summary Counts):
- **`real_llm_count`**: `0` (0/30 ca được sinh từ mô hình AI thật)
- **`mock_count`**: `30` (30/30 ca xuất xứ từ engine mock cục bộ)
- **`gold_copied_count`**: `30` (30/30 ca chứa dữ liệu sao chép trực tiếp từ Ground Truth)
- **`fallback_count`**: `0`
- **`cached_count`**: `0`
- **`unknown_count`**: `0`

> [!CAUTION]
> **PHÁT HIỆN CỐT LÕI (CRITICAL FINDING)**:  
> Trên cả 10/10 ca thuộc tập Frozen Test (`vct-481` đến `vct-490`), **toàn bộ các trường dự đoán sư phạm quan trọng** (`bug_status`, `error_category`, `bug_type`, `bug_location`, `evidence`, `knowledge_components`, `possible_misconception`, `hint_1`, `hint_2`, `hint_3`) **đều là bản sao chép nguyên văn 100% từ nhãn vàng ground truth** do tác giả biên soạn (`COPIED_FROM_GROUND_TRUTH`).  
> Không có bất kỳ dấu vết nào của quá trình suy luận mô hình ngôn ngữ lớn trong các kết quả này.

---

## 2. BẢNG TỔNG HỢP NGUỒN GỐC 30 CA KIỂM TOÁN

| STT | Sample ID | Split | Hệ thống | Nguồn gốc (`Origin`) | Trạng thái sao chép nhãn vàng | Diag Acc | Loc Acc | KC F1 | Leakage |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | `vct-001` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 2 | `vct-002` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 3 | `vct-003` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 4 | `vct-004` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 5 | `vct-005` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 6 | `vct-006` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 7 | `vct-007` | `dev` | Proposed C | `MOCK` | **PARTIAL COPY** | SAI | SAI | `0.00` | `False` |
| 8 | `vct-008` | `dev` | Proposed C | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 9 | `vct-009` | `dev` | Proposed C | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 10 | `vct-010` | `dev` | Proposed C | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 11 | `vct-361` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 12 | `vct-362` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 13 | `vct-363` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 14 | `vct-364` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 15 | `vct-365` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 16 | `vct-366` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 17 | `vct-367` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 18 | `vct-368` | `validation` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 19 | `vct-369` | `validation` | Proposed D | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 20 | `vct-370` | `validation` | Proposed D | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 21 | `vct-481` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 22 | `vct-482` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 23 | `vct-483` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 24 | `vct-484` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 25 | `vct-485` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 26 | `vct-486` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 27 | `vct-487` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 28 | `vct-488` | `test` | Proposed D | `MOCK` | **100% COPIED** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 29 | `vct-489` | `test` | Proposed D | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |
| 30 | `vct-490` | `test` | Proposed D | `MOCK` | **PARTIAL COPY** | ĐÚNG | ĐÚNG | `1.00` | `False` |

---

## 3. CHI TIẾT 10 CA FROZEN TEST (OFFLINE RECONSTRUCTION)

### Ca kiểm toán: `vct-481` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `compile_error` | Loại lỗi: `uninstantiated_object_reference`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `compile_error` | `compile_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `uninstantiated_object_reference` | `uninstantiated_object_reference` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 19, 'end_line': 19, 'symbol': 'item.StackLoad'}` | `{'file': 'Program.cs', 'start_line': 19, 'end_line': 19, 'symbol': 'item.StackLoad'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `item.StackLoad();` | `item.StackLoad();` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Classes', 'OOP.Instantiation', 'OOP.NullReference']` | `['OOP.Classes', 'OOP.Instantiation', 'OOP.NullReference']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Hãy kiểm tra xem biến đối tượng của bạn ...` | `Hãy kiểm tra xem biến đối tượng của bạn ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Biến `WarehousePallet item` chưa được kh...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-482` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `compile_error` | Loại lỗi: `inaccessible_private_field`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `compile_error` | `compile_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `inaccessible_private_field` | `inaccessible_private_field` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 13, 'end_line': 13, 'symbol': 'obj.palletcode'}` | `{'file': 'Program.cs', 'start_line': 13, 'end_line': 13, 'symbol': 'obj.palletcode'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `Console.WriteLine(obj.palletcode);` | `Console.WriteLine(obj.palletcode);` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Fields', 'OOP.AccessModifiers', 'OOP.Properties']` | `['OOP.Fields', 'OOP.AccessModifiers', 'OOP.Properties']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Hãy quan sát mức độ truy cập (access mod...` | `Hãy quan sát mức độ truy cập (access mod...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Trường `palletcode` được khai báo `priva...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-483` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `runtime_error` | Loại lỗi: `recursive_property_accessor`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `runtime_error` | `runtime_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `recursive_property_accessor` | `recursive_property_accessor` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 11, 'end_line': 11, 'symbol': 'WarehousePallet.LoadWeightKg'}` | `{'file': 'Program.cs', 'start_line': 11, 'end_line': 11, 'symbol': 'WarehousePallet.LoadWeightKg'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `return LoadWeightKg;` | `return LoadWeightKg;` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Properties', 'OOP.BackingFields', 'OOP.Recursion']` | `['OOP.Properties', 'OOP.BackingFields', 'OOP.Recursion']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Hãy chú ý biến mà bạn đang trả về trong ...` | `Hãy chú ý biến mà bạn đang trả về trong ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Getter và Setter của `LoadWeightKg` đang...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-484` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `logic_error` | Loại lỗi: `unassigned_field_shadowing`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `logic_error` | `logic_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `unassigned_field_shadowing` | `unassigned_field_shadowing` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 11, 'end_line': 11, 'symbol': 'WarehousePallet.WarehousePallet'}` | `{'file': 'Program.cs', 'start_line': 11, 'end_line': 11, 'symbol': 'WarehousePallet.WarehousePallet'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `loadweightkg = loadweightkg;` | `loadweightkg = loadweightkg;` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Constructors', 'OOP.ThisKeyword', 'OOP.VariableShadowing']` | `['OOP.Constructors', 'OOP.ThisKeyword', 'OOP.VariableShadowing']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Hãy xem xét câu lệnh gán bên trong hàm t...` | `Hãy xem xét câu lệnh gán bên trong hàm t...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Dòng lệnh `loadweightkg = loadweightkg;`...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-485` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `compile_error` | Loại lỗi: `return_type_mismatch`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `compile_error` | `compile_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `return_type_mismatch` | `return_type_mismatch` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 10, 'end_line': 10, 'symbol': 'WarehousePallet.StackLoad'}` | `{'file': 'Program.cs', 'start_line': 10, 'end_line': 10, 'symbol': 'WarehousePallet.StackLoad'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `return true;` | `return true;` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Methods', 'OOP.ReturnTypes', 'OOP.Parameters']` | `['OOP.Methods', 'OOP.ReturnTypes', 'OOP.Parameters']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Hãy so sánh kiểu trả về ở dòng khai báo ...` | `Hãy so sánh kiểu trả về ở dòng khai báo ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Phương thức `StackLoad` được khai báo ki...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-486` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `logic_error` | Loại lỗi: `missing_domain_validation`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `logic_error` | `logic_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `missing_domain_validation` | `missing_domain_validation` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 9, 'end_line': 9, 'symbol': 'WarehousePallet.StackLoad'}` | `{'file': 'Program.cs', 'start_line': 9, 'end_line': 9, 'symbol': 'WarehousePallet.StackLoad'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `LoadWeightKg += amount;` | `LoadWeightKg += amount;` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Encapsulation', 'OOP.DataValidation', 'OOP.ClassInvariants']` | `['OOP.Encapsulation', 'OOP.DataValidation', 'OOP.ClassInvariants']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Điều gì sẽ xảy ra nếu người dùng truyền ...` | `Điều gì sẽ xảy ra nếu người dùng truyền ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Phương thức `StackLoad` trực tiếp cộng g...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-487` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `compile_error` | Loại lỗi: `static_context_instance_member_access`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `compile_error` | `compile_error` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `static_context_instance_member_access` | `static_context_instance_member_access` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 15, 'end_line': 15, 'symbol': 'WarehousePallet.StackLoad'}` | `{'file': 'Program.cs', 'start_line': 15, 'end_line': 15, 'symbol': 'WarehousePallet.StackLoad'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `WarehousePallet.StackLoad();` | `WarehousePallet.StackLoad();` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.StaticMembers', 'OOP.InstanceMembers', 'OOP.StaticContext']` | `['OOP.StaticMembers', 'OOP.InstanceMembers', 'OOP.StaticContext']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Phương thức `{action}` có từ khóa `stati...` | `Phương thức `{action}` có từ khóa `stati...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Phương thức `StackLoad` là phương thức i...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-488` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `conceptual_misuse` | Loại lỗi: `missing_override_polymorphism`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `has_bug` | `has_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `conceptual_misuse` | `conceptual_misuse` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `missing_override_polymorphism` | `missing_override_polymorphism` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `{'file': 'Program.cs', 'start_line': 5, 'end_line': 5, 'symbol': 'SpecialWarehousePallet.StackLoad'}` | `{'file': 'Program.cs', 'start_line': 5, 'end_line': 5, 'symbol': 'SpecialWarehousePallet.StackLoad'}` | `COPIED_FROM_GROUND_TRUTH` |
  | `evidence` | `public void StackLoad()` | `public void StackLoad()` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.Inheritance', 'OOP.Polymorphism', 'OOP.VirtualOverride']` | `['OOP.Inheritance', 'OOP.Polymorphism', 'OOP.VirtualOverride']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Khi gọi phương thức qua biến tham chiếu ...` | `Khi gọi phương thức qua biến tham chiếu ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Thiếu từ khóa `virtual` ở lớp cha và `ov...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-489` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `no_bug` | Loại lỗi: `no_bug`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `no_bug` | `no_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `no_bug` | `no_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `no_bug` | `no_bug` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `None` | `None` | `STATIC_CONSTANT` |
  | `evidence` | `None` | `None` | `STATIC_CONSTANT` |
  | `knowledge_components` | `['OOP.Classes', 'OOP.Properties', 'OOP.Constructors', 'OOP.CleanCode']` | `['OOP.Classes', 'OOP.Properties', 'OOP.Constructors', 'OOP.CleanCode']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Mã nguồn của bạn đã giải quyết đúng và đ...` | `Mã nguồn của bạn đã giải quyết đúng và đ...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Mã nguồn hoàn toàn chính xác, đáp ứng đầ...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

### Ca kiểm toán: `vct-490` (Split: Test | Hệ thống: Proposed D)
- **Vấn đề / Mã lỗi**: `insufficient_context` | Loại lỗi: `insufficient_context`
- **Nguồn gốc dự đoán**: `MOCK` (Tệp: `backend/app/evaluation/runner.py:331-342`)
- **Bảng đối chiếu từng trường dự đoán và nhãn vàng**:
  | Trường dữ liệu | Giá trị Ground Truth | Giá trị Prediction | Phân loại Provenance |
  |---|---|---|:---:|
  | `bug_status` | `insufficient_context` | `insufficient_context` | `COPIED_FROM_GROUND_TRUTH` |
  | `error_category` | `insufficient_context` | `insufficient_context` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_type` | `insufficient_context` | `insufficient_context` | `COPIED_FROM_GROUND_TRUTH` |
  | `bug_location` | `None` | `None` | `STATIC_CONSTANT` |
  | `evidence` | `var currentItem = GetActiveWarehousePallet();` | `var currentItem = GetActiveWarehousePallet();` | `COPIED_FROM_GROUND_TRUTH` |
  | `knowledge_components` | `['OOP.ProgramStructure', 'OOP.ContextSufficiency']` | `['OOP.ProgramStructure', 'OOP.ContextSufficiency']` | `COPIED_FROM_GROUND_TRUTH` |
  | `hint_1` | `Đoạn mã hiện tại chưa cung cấp đầy đủ đị...` | `Đoạn mã hiện tại chưa cung cấp đầy đủ đị...` | `COPIED_FROM_GROUND_TRUTH` |
  | `reference_diagnosis` | `...` | `Đoạn mã bị cắt đoạn: thiếu định nghĩa lớ...` | `COPIED_FROM_GROUND_TRUTH` |
- **Đánh giá kiểm toán viên**: 100% các giá trị dự đoán được sao chép nguyên văn từ đối tượng `sample` ground truth của bộ dữ liệu.

---

## 4. KẾT LUẬN KIỂM TOÁN

Kiểm toán nguồn gốc 30 ca (APT-045) đã xác nhận dứt khoát bằng chứng vật lý:
1. **Không có suy luận thật từ LLM**: Toàn bộ các kết quả dự đoán được ghi trong các thư mục runs chính thức đều bắt nguồn từ mock generator trong `runner.py`.
2. **Xác nhận gian lận sao chép nhãn vàng**: Toàn bộ 10/10 mẫu Frozen Test của Proposed D đều lấy 100% dữ liệu nhãn vàng gắn sang trường dự đoán, giải thích lý do tại sao các chỉ số đạt điểm số tuyệt đối 100% một cách giả tạo.
3. Tệp JSON chi tiết `artifacts/audit/provenance_30_cases.json` lưu trữ đầy đủ hồ sơ của cả 30 ca kiểm toán phục vụ đối chiếu độc lập.
