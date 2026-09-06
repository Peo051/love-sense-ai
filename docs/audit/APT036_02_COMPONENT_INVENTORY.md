# APT-036.2: BẢNG KIỂM KÊ TOÀN DIỆN CÁC THÀNH PHẦN ĐÁNH GIÁ (EVALUATION COMPONENT INVENTORY)

**Vai trò:** Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Tổng số thành phần kiểm kê:** 34 thành phần phân bố trên 14 hạng mục kiến trúc  

---

## 1. Tóm Tắt Phân Loại 14 Hạng Mục Kiến Trúc

| Hạng mục (Category) | Số lượng tệp/thành phần | Được phép đọc Ground Truth? | Ghi chú kiểm toán |
| :--- | :---: | :---: | :--- |
| **DATASET** | 3 | **CÓ (CẦN KIỂM SOÁT)** | Tập dữ liệu benchmark chính thức gồm 600 ca bài tập C# OOP k... |
| **DATASET LOADER** | 2 | **CÓ (CẦN KIỂM SOÁT)** | Tải dataset từ tệp JSONL, lọc theo split được chọn và tính t... |
| **MODEL INPUT BUILDER** | 2 | KHÔNG | Xây dựng bối cảnh đầu vào cho gia sư AI (phân tách submitted... |
| **PROMPT BUILDER** | 3 | KHÔNG | Xây dựng chuỗi prompt đóng băng có gắn phiên bản cho 4 hệ th... |
| **EVALUATION RUNNER** | 3 | **CÓ (CẦN KIỂM SOÁT)** | Bộ điều phối thực nghiệm đánh giá trung tâm cho VietCSharpTu... |
| **LLM PROVIDER CLIENT** | 1 | KHÔNG | Lớp tích hợp API gọi mô hình ngôn ngữ lớn (OpenAI Chat Compl... |
| **MOCK / FALLBACK** | 3 | **CÓ (CẦN KIỂM SOÁT)** | Harness giả lập phản hồi của mô hình phục vụ kiểm thử đường ... |
| **OUTPUT PARSER** | 1 | KHÔNG | Định nghĩa Pydantic schema để parse và xác thực phản hồi có ... |
| **OUTPUT VALIDATOR** | 3 | KHÔNG | Kiểm định đầu ra của gia sư: kiểm tra cú pháp JSON, kiểm tra... |
| **PREDICTION STORAGE** | 1 | KHÔNG | Thư mục lưu trữ các tệp kết quả dự đoán (predictions.jsonl) ... |
| **METRIC CALCULATOR** | 3 | **CÓ (CẦN KIỂM SOÁT)** | Bộ công cụ tính toán 11 chỉ số sư phạm cốt lõi và tài nguyên... |
| **ABLATION CONFIGURATION** | 2 | **CÓ (CẦN KIỂM SOÁT)** | Định nghĩa 5 cấu hình triệt tiêu độc lập (FULL, NO_STUDENT_M... |
| **MANIFEST / PROVENANCE** | 1 | KHÔNG | Thư mục lưu trữ các bản sao run manifest bất biến (immutable... |
| **TEST-ONLY INFRASTRUCTURE** | 6 | **CÓ (CẦN KIỂM SOÁT)** | Kiểm định đơn vị cho EvaluationRunner: kiểm tra nạp dữ liệu,... |

---

## 2. Bảng Kiểm Kê Chi Tiết Từng Thành Phần

| STT | Hạng mục | Đường dẫn tệp | Mục đích chính | Prod? | Research? | Test-only? | Đọc Ground Truth? |
| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `DATASET` | `data/vietcsharptutor/vietcsharptutor_600.jsonl` | Tập dữ liệu benchmark chính thức gồm 600 ca bài tập C# OOP kèm 25 trường nhãn vàng chuẩn. | No | Yes | No | **CÓ** |
| 2 | `DATASET` | `data/vietcsharptutor/examples.jsonl` | Tập ví dụ minh họa và mẫu kiểm thử định dạng schema cho VietCSharpTutor. | No | Yes | Yes | **CÓ** |
| 3 | `DATASET` | `data/vietcsharptutor/schema.json` | JSON Schema định nghĩa cấu trúc hợp lệ cho 25 trường dữ liệu của VietCSharpTutor. | No | Yes | No | Không |
| 4 | `DATASET LOADER` | `backend/app/evaluation/runner.py` | Tải dataset từ tệp JSONL, lọc theo split được chọn và tính toán SHA256 checksum bảo vệ tính toàn vẹn. | No | Yes | No | **CÓ** |
| 5 | `DATASET LOADER` | `scripts/validate_vietcsharptutor.py` | Nạp toàn bộ dataset JSONL vào bộ nhớ để kiểm tra cú pháp, schema và phân chia split. | No | Yes | No | **CÓ** |
| 6 | `MODEL INPUT BUILDER` | `backend/app/tutor/context_builder.py` | Xây dựng bối cảnh đầu vào cho gia sư AI (phân tách submitted code evidence và learner context, kiểm soát ngân sách token). | Yes | No | No | Không |
| 7 | `MODEL INPUT BUILDER` | `backend/app/services/prompt_builder.py` | Xây dựng prompt chung cho các dịch vụ phân tích. | Yes | No | No | Không |
| 8 | `PROMPT BUILDER` | `backend/app/evaluation/prompts.py` | Xây dựng chuỗi prompt đóng băng có gắn phiên bản cho 4 hệ thống đánh giá (A, B, C, D). | No | Yes | No | Không |
| 9 | `PROMPT BUILDER` | `backend/app/tutor/prompts/diagnosis_v1.py` | Đặc tả cấu trúc prompt chẩn đoán lỗi OOP trong môi trường sản xuất. | Yes | No | No | Không |
| 10 | `PROMPT BUILDER` | `backend/app/tutor/prompts/system_policy_v1.py` | Đặc tả system prompt chính sách sư phạm 3 tầng gợi ý trong sản xuất. | Yes | No | No | Không |
| 11 | `EVALUATION RUNNER` | `backend/app/evaluation/runner.py` | Bộ điều phối thực nghiệm đánh giá trung tâm cho VietCSharpTutor: nạp dữ liệu, sinh dự đoán, ghi predictions.jsonl và manifest.json. | No | Yes | No | **CÓ** |
| 12 | `EVALUATION RUNNER` | `scripts/run_evaluation.py` | Giao diện dòng lệnh (CLI) để khởi chạy EvaluationRunner cho một hệ thống (A, B, C, D) trên một split (dev, val, test). | No | Yes | No | **CÓ** |
| 13 | `EVALUATION RUNNER` | `scripts/execute_frozen_protocol.py` | Kịch bản tự động thực thi toàn bộ giao thức đóng băng: kiểm tra git commit, chạy validation trước, sau đó chạy test một lần duy nhất. | No | Yes | No | **CÓ** |
| 14 | `LLM PROVIDER CLIENT` | `backend/app/tutor/provider.py` | Lớp tích hợp API gọi mô hình ngôn ngữ lớn (OpenAI Chat Completion) trong ứng dụng gia sư sản xuất. | Yes | No | No | Không |
| 15 | `MOCK / FALLBACK` | `backend/app/evaluation/runner.py` | Harness giả lập phản hồi của mô hình phục vụ kiểm thử đường ống (Mock Mode). | No | Yes | No | **CÓ** |
| 16 | `MOCK / FALLBACK` | `backend/app/evaluation/ablation.py` | Harness giả lập phản hồi cho các cấu hình triệt tiêu ablation trong mock mode. | No | Yes | No | **CÓ** |
| 17 | `MOCK / FALLBACK` | `backend/app/core/config.py` | Cấu hình biến môi trường ứng dụng, chứa cờ MOCK_LLM. | Yes | No | No | Không |
| 18 | `OUTPUT PARSER` | `backend/app/schemas/tutor_schema.py` | Định nghĩa Pydantic schema để parse và xác thực phản hồi có cấu trúc JSON từ LLM. | Yes | Yes | No | Không |
| 19 | `OUTPUT VALIDATOR` | `backend/app/tutor/validator.py` | Kiểm định đầu ra của gia sư: kiểm tra cú pháp JSON, kiểm tra evidence trích xuất nguyên văn, kiểm tra rò rỉ mã giải pháp. | Yes | No | No | Không |
| 20 | `OUTPUT VALIDATOR` | `backend/app/tutor/leakage_guard.py` | Bộ lọc ngăn chặn rò rỉ mã giải pháp trong các gợi ý bậc 1 và 2. | Yes | No | No | Không |
| 21 | `OUTPUT VALIDATOR` | `backend/app/tutor/evidence_grounding.py` | Kiểm tra chuỗi bằng chứng (evidence) có nằm nguyên văn trong mã nguồn học viên hay không. | Yes | No | No | Không |
| 22 | `PREDICTION STORAGE` | `runs/` | Thư mục lưu trữ các tệp kết quả dự đoán (predictions.jsonl) và manifest của tất cả các đợt chạy thực nghiệm. | No | Yes | No | Không |
| 23 | `METRIC CALCULATOR` | `backend/app/evaluation/metrics.py` | Bộ công cụ tính toán 11 chỉ số sư phạm cốt lõi và tài nguyên hoàn toàn offline từ predictions và ground truth. | No | Yes | No | **CÓ** |
| 24 | `METRIC CALCULATOR` | `scripts/evaluate_metrics.py` | CLI chạy tính toán metrics offline cho một run hoặc thư mục run. | No | Yes | No | **CÓ** |
| 25 | `METRIC CALCULATOR` | `scripts/analyze_results.py` | Phân tích kết quả thực nghiệm hoàn chỉnh: tính khoảng tin cậy bootstrap, kiểm định paired McNemar, so sánh ablation. | No | Yes | No | **CÓ** |
| 26 | `ABLATION CONFIGURATION` | `backend/app/evaluation/ablation.py` | Định nghĩa 5 cấu hình triệt tiêu độc lập (FULL, NO_STUDENT_MODEL, NO_PROGRESSIVE_HINT, NO_STRUCTURED_DIAGNOSIS, DIRECT_BASELINE) và runner thực thi. | No | Yes | No | **CÓ** |
| 27 | `ABLATION CONFIGURATION` | `scripts/run_ablation.py` | CLI khởi chạy các thí nghiệm ablation theo tên cấu hình và split. | No | Yes | No | **CÓ** |
| 28 | `MANIFEST / PROVENANCE` | `manifests/` | Thư mục lưu trữ các bản sao run manifest bất biến (immutable manifests) ghi nhận hash dataset, git commit, seed, config. | No | Yes | No | Không |
| 29 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/test_evaluation_runner.py` | Kiểm định đơn vị cho EvaluationRunner: kiểm tra nạp dữ liệu, tạo manifest, sinh dự đoán mock. | No | No | Yes | **CÓ** |
| 30 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/test_ablation.py` | Kiểm định đơn vị cho AblationRunner và 5 cấu hình triệt tiêu. | No | No | Yes | **CÓ** |
| 31 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/test_tutoring_metrics.py` | Kiểm định đơn vị cho TutoringMetricsSuite với các ví dụ tính tay. | No | No | Yes | **CÓ** |
| 32 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/test_taint_isolation.py` | Kiểm định cô lập nhãn vàng: xác minh các chuỗi sentinel ground-truth không lọt vào prompt. | No | No | Yes | **CÓ** |
| 33 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/test_dataset_validator.py` | Kiểm định các quy tắc validation của DatasetValidator. | No | No | Yes | **CÓ** |
| 34 | `TEST-ONLY INFRASTRUCTURE` | `backend/tests/conftest.py` | Cấu hình fixture chung cho toàn bộ pytest suite. | No | No | Yes | Không |

---

## 3. Phân Tích Rủi Ro Truy Cập Nhãn Vàng (Ground-Truth Access Audit)

Kiểm toán viên xác định danh sách các tệp có khả năng truy cập trực tiếp nhãn vàng (`can_access_ground_truth = True`) và mức độ rủi ro tương ứng:

| Tệp thành phần | Hạng mục | Bản chất truy cập Ground Truth | Đánh giá mức độ rủi ro |
| :--- | :--- | :--- | :--- |
| `backend/app/evaluation/runner.py` | EVALUATION RUNNER / MOCK | Truy cập `sample` để gán vào kết quả dự đoán của Proposed D | **CRITICAL: Rò rỉ nhãn vàng trực tiếp** |
| `backend/app/evaluation/ablation.py` | ABLATION CONFIG / MOCK | Truy cập `sample` để gán vào kết quả cấu hình FULL | **CRITICAL: Rò rỉ nhãn vàng trực tiếp** |
| `backend/app/evaluation/metrics.py` | METRIC CALCULATOR | Đối chiếu predictions với ground truth để tính toán Accuracy, F1 | **HỢP LỆ: Hoạt động offline sau khi đã sinh dự đoán** |
| `scripts/validate_vietcsharptutor.py` | OUTPUT VALIDATOR | Kiểm tra tính hợp lệ schema của 25 trường | **HỢP LỆ: Tiền kiểm định dữ liệu** |
| `backend/tests/test_taint_isolation.py` | TEST INFRASTRUCTURE | Kiểm thử cô lập nhãn vàng bằng chuỗi sentinel | **HỢP LỆ: Kiểm thử bảo vệ** |

---

## 4. Tách Bạch Hạ Tầng Kiểm Thử & Mã Nguồn Sản Xuất (Infrastructure Separation)

Kiểm toán viên xác nhận:

1. **Tách biệt sản xuất (Production Isolation):** Các module sản xuất tại `backend/app/tutor/` (gồm `context_builder.py`, `validator.py`, `leakage_guard.py`, `provider.py`) KHÔNG hề đọc tệp `vietcsharptutor_600.jsonl` và KHÔNG có quyền truy cập nhãn vàng.

2. **Hạ tầng Test-only:** Toàn bộ các tệp trong `backend/tests/` được cách ly hoàn toàn khỏi luồng thực thi production.

3. **Lỗ hổng Mock Harness trong Nghiên cứu:** Lỗi rò rỉ nhãn vàng khu trú hoàn toàn bên trong lớp `runner.py` và `ablation.py` của bộ sinh mock harness nghiên cứu.
