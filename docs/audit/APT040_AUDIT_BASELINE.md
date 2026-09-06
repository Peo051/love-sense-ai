# APT-040: ĐÓNG BĂNG ĐIỂM BẮT ĐẦU KIỂM TOÁN ĐÁNH GIÁ (FREEZE EVALUATION AUDIT BASELINE)

**Vai trò:** Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Nhánh kiểm toán:** `audit/evaluation-integrity-v1`  
**Thời gian đóng băng:** 2026-09-06T15:56:53.601252+00:00  

> [!IMPORTANT]

> **Mục đích:** Khóa bất biến toàn bộ trạng thái mã nguồn, tập dữ liệu, cấu hình thực nghiệm và môi trường trước khi thực hiện bất kỳ sửa chữa nào liên quan đến evaluation pipeline. Không sửa đổi hành vi mã nguồn, không gọi lại mô hình LLM trên test split.

---

## 1. Trạng Thái Git (Git State)

| Thuộc tính Git | Giá trị thực tế | Nhận xét kiểm toán |
| :--- | :--- | :--- |
| **Current Branch** | `audit/evaluation-integrity-v1` | Nhánh kiểm toán độc lập |
| **Current HEAD Commit** | `3035e069d26892a010276993bdc452c9a458f45c` | Khởi tạo từ release v1.0 |
| **Release Tag Commit** | `3035e069d26892a010276993bdc452c9a458f45c` | Tag `codesense-research-v1.0` |
| **Đối chiếu Commit** | **KHỚP TUYỆT ĐỐI** (`True`) | Trạng thái mã nguồn đóng băng hoàn hảo |
| **Release Tags liên quan** | `codesense-research-v1.0, love-sense-ai-final` | Được bảo tồn nguyên vẹn |
| **Working Tree Status** | Sạch sẽ, bảo vệ tệp audit | Không có mã nguồn bị sửa đổi |

### Các tệp untracked liên quan đến kiểm toán:
- `artifacts/`
- `backend/tests/test_taint_isolation.py`
- `docs/audit/`

---

## 2. Bảng Checksum SHA-256 Các Tài Sản Nghiên Cứu (Research Asset Hashes)

### A. Bộ dữ liệu VietCSharpTutor & Các phân vùng (Splits)
| Thành phần dữ liệu | Số mẫu | SHA-256 Checksum |
| :--- | :---: | :--- |
| **VietCSharpTutor Dataset toàn bộ (`vietcsharptutor_600.jsonl`)** | 600 | `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed` |
| **Phân vùng `dev`** | 360 | `4883098109f85fa42e1e7e874c2f11ddc51f59987e931dcda388ce862a98a52b` |
| **Phân vùng `validation`** | 120 | `d9b3ad1339228aa4c47c9444def07ab013cef8498bcc244afbe24a7218b3349a` |
| **Phân vùng `test` (Frozen Test Split)** | 120 | `65aa09f289f3db70846730b3b73a75395b61b50a2b33412ddd2a7c6aa6a39544` |

### B. Cấu hình đánh giá, Prompts, Metrics & Scripts
| Phân loại | Tên tệp | Đường dẫn | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `dataset` | `vietcsharptutor_600.jsonl` | `data/vietcsharptutor/vietcsharptutor_600.jsonl` | `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed` |
| `dataset` | `schema.json` | `data/vietcsharptutor/schema.json` | `7c3b25080d2ce64dee76e5d62fb475a4bb8f28abc65535c081d644365e90cd32` |
| `dataset` | `examples.jsonl` | `data/vietcsharptutor/examples.jsonl` | `aa84eeeae24dec3b0827b248ba43568401cf7f0c12660ed236a634ad4dbd69f4` |
| `evaluation_configuration` | `runner.py` | `backend/app/evaluation/runner.py` | `a1ffa68f5fa3d38fa67d2b8b5c52afcd227288da54c0c63b4bcea60a1474e428` |
| `evaluation_configuration` | `ablation.py` | `backend/app/evaluation/ablation.py` | `fb824572145de69abcf03909914b7413f1399017a74e9a68d1a247f093e5e740` |
| `evaluation_prompts` | `prompts.py` | `backend/app/evaluation/prompts.py` | `bf658267576906fec5a423a0b7f62c774a8e12a34955cfedb0ad29d3b3dc741b` |
| `ablation_configurations` | `ablation.py` | `backend/app/evaluation/ablation.py` | `fb824572145de69abcf03909914b7413f1399017a74e9a68d1a247f093e5e740` |
| `metric_implementation` | `metrics.py` | `backend/app/evaluation/metrics.py` | `104b732ca17fab64ec4251156209bf1e01f1ed3dcd96d644f97a191caedbaeb1` |
| `research_runners` | `run_evaluation.py` | `scripts/run_evaluation.py` | `2446811c495ec943c856439ee9d6f74e103e002243f223ee96cbeffb374c060d` |
| `research_runners` | `run_ablation.py` | `scripts/run_ablation.py` | `6bc6214d1bf39f1d7e895f430d0a332b90fbd1c2f216663d336481bca06c1dad` |
| `research_runners` | `evaluate_metrics.py` | `scripts/evaluate_metrics.py` | `a32e8b2f4aac2de1093ad5e0a14a8d4424d0bcf1f647812780870f763c446291` |
| `research_runners` | `analyze_results.py` | `scripts/analyze_results.py` | `768256600aa18b71134a0191715e4130c879f4df61a1986ac7edae57c4b7b90f` |
| `frozen_protocol_script` | `execute_frozen_protocol.py` | `scripts/execute_frozen_protocol.py` | `77dcdbc1adf03555d05eaf92a727940a48d7998c897b7dcf04d959f6cb8f21cd` |
| `dependency_files` | `backend_requirements.txt` | `backend/requirements.txt` | `99721287c25c9f558851465a8f9f8009bc633c46d2efa669c52c7f82353f2716` |
| `dependency_files` | `frontend_package.json` | `frontend/package.json` | `c8ac8691d4788849eaf55d155a92da526611ffea50b8e247f05762cca9f2284e` |
| `dependency_files` | `frontend_package_lock.json` | `frontend/package-lock.json` | `8ab4b263f3e774da2b07242a6519c31241c701f7b87fc789a9d5492cddbd8107` |

---

## 3. Môi Trường Thực Thi (Clean-Room Environment)

| Thành phần môi trường | Phiên bản thực tế | Ghi chú kiểm toán |
| :--- | :--- | :--- |
| **Hệ điều hành (OS)** | `Windows 11 (Build 10.0.26200)` | Môi trường máy trạm Windows NT |
| **Python Version** | `3.13.9` | Backend Python Virtualenv |
| **Node.js Version** | `v24.14.0` | Frontend Next.js Runtime |
| **NPM Version** | `11.9.0` | Quản lý gói frontend |
| **.NET SDK Version** | `10.0.400` | Trình biên dịch/chạy C# Roslyn |

---

## 4. Cấu Hình Hệ Thống Nghiên Cứu (Research Configuration)

- **Tên Provider cấu hình:** `mock`
- **Mã mô hình yêu cầu (Requested Model):** `mock-tutor-v1`
- **Cấu hình Mock:** `Mô phỏng tĩnh để kiểm định đường ống phần mềm và đánh giá thực nghiệm offline` (`mock_mode = True`)
- **Cơ chế Fallback:** `deterministic_category_fallback` (0 network retries)
- **Cơ chế Cache:** `local_filesystem` (Lưu cục bộ tại `runs/`)
- **Chính sách Retry:** `no_network_retry_on_mock`

### Bảng đối chiếu tham số 4 hệ thống đánh giá:
| Hệ thống | Phiên bản Prompt | Nhiệt độ ($T$) | Max Tokens | Chẩn đoán cấu trúc | Gợi ý tăng dần | Bối cảnh học viên |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Baseline A: Direct LLM Debugging Prompt** | `v1.0-direct-debug` | 0.7 | 1024 | False | False | False |
| **Baseline B: Generic Tutor Prompt** | `v1.0-generic-tutor` | 0.7 | 1024 | False | False | False |
| **Proposed C: Structured Diagnosis + Progressive Hints** | `v1.0-structured-progressive` | 0.2 | 1024 | True | True | False |
| **Proposed D: Structured Diagnosis + Progressive Hints + Student Context** | `v1.0-contextual-adaptive` | 0.2 | 1024 | True | True | True |

---

## 5. Cam Kết Liêm Chính & Tiêu Chuẩn Nghiệm Thu (Acceptance Verification)

- [x] **Frozen release commit recorded:** Đã ghi nhận SHA `3035e069d26892a010276993bdc452c9a458f45c`.
- [x] **Dataset hash recorded:** Đã tính toán SHA-256 cho toàn bộ dataset và 3 splits.
- [x] **Evaluation file hashes recorded:** Đã tính toán SHA-256 cho runner, prompts, ablation, metrics, scripts, dependency files.
- [x] **Environment recorded:** Đã ghi nhận OS, Python, Node, NPM, dotnet.
- [x] **Provider/model identifiers recorded:** Đã ghi nhận provider `mock` và model `mock-tutor-v1`.
- [x] **No secret exposed:** Xác nhận 100% không có API key hay thông tin bí mật nào bị lộ.
- [x] **No research result modified:** Giữ nguyên trạng các tệp kết quả trong `results/` và `runs/`.
- [x] **No frozen test LLM call performed:** Không thực hiện bất kỳ lệnh gọi LLM mới nào trên test split.