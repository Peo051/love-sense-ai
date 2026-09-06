# APT-036.1: ĐIỂM BẮT ĐẦU KIỂM TOÁN ĐÓNG BĂNG (IMMUTABLE AUDIT BASELINE)

**Vai trò:** Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Nhánh kiểm toán:** `audit/evaluation-integrity-v1`  
**Thời điểm tạo:** 2026-09-06T11:18:10.728720+00:00  

---

## 1. Trạng Thái Git & Release Commit

| Thuộc tính Git | Giá trị thực tế | Ghi chú kiểm toán |
| :--- | :--- | :--- |
| **Current Branch** | `audit/evaluation-integrity-v1` | Nhánh kiểm toán độc lập |
| **HEAD Commit SHA** | `3035e069d26892a010276993bdc452c9a458f45c` | Khởi tạo từ release v1.0 |
| **Release Tag Commit** | `3035e069d26892a010276993bdc452c9a458f45c` | Tag `codesense-research-v1.0` |
| **Khớp Commit tuyệt đối** | **True** | Điểm neo mã nguồn hoàn toàn đồng nhất |
| **Các Tags tồn tại** | `codesense-research-v1.0, love-sense-ai-final` | Được bảo toàn nguyên vẹn |

---

## 2. Checksum Dữ Liệu & Phân Vùng Đóng Băng

| Phân vùng / Tập dữ liệu | Số lượng mẫu | SHA-256 Checksum |
| :--- | :---: | :--- |
| **Toàn bộ dataset (`vietcsharptutor_600.jsonl`)** | 600 | `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed` |
| **Phân vùng `dev`** | 360 | `4883098109f85fa42e1e7e874c2f11ddc51f59987e931dcda388ce862a98a52b` |
| **Phân vùng `validation`** | 120 | `d9b3ad1339228aa4c47c9444def07ab013cef8498bcc244afbe24a7218b3349a` |
| **Phân vùng `test` (Frozen Test Split)** | 120 | `65aa09f289f3db70846730b3b73a75395b61b50a2b33412ddd2a7c6aa6a39544` |

---

## 3. Checksum Tệp Cấu Hình, Prompt & Mã Nguồn Nghiên Cứu

| Nhóm thành phần | Tên tệp | Đường dẫn | SHA-256 Checksum |
| :--- | :--- | :--- | :--- |
| `evaluation_config` | `runner.py` | `backend/app/evaluation/runner.py` | `a1ffa68f5fa3d38fa67d2b8b5c52afcd227288da54c0c63b4bcea60a1474e428` |
| `evaluation_config` | `ablation.py` | `backend/app/evaluation/ablation.py` | `fb824572145de69abcf03909914b7413f1399017a74e9a68d1a247f093e5e740` |
| `evaluation_config` | `metrics.py` | `backend/app/evaluation/metrics.py` | `104b732ca17fab64ec4251156209bf1e01f1ed3dcd96d644f97a191caedbaeb1` |
| `evaluation_prompts` | `prompts.py` | `backend/app/evaluation/prompts.py` | `bf658267576906fec5a423a0b7f62c774a8e12a34955cfedb0ad29d3b3dc741b` |
| `research_scripts` | `validate_vietcsharptutor.py` | `scripts/validate_vietcsharptutor.py` | `a79a7c52e0a6bba02deeb5d374b54bccecd7e5d8326492425f057c29c5392821` |
| `research_scripts` | `generate_vietcsharptutor_600.py` | `scripts/generate_vietcsharptutor_600.py` | `a0b5a1924602e7e62fe8c2268bad9fd2b93dbd3d627f914f7b7ff1f3b5f88903` |
| `research_scripts` | `execute_frozen_protocol.py` | `scripts/execute_frozen_protocol.py` | `77dcdbc1adf03555d05eaf92a727940a48d7998c897b7dcf04d959f6cb8f21cd` |
| `research_scripts` | `evaluate_metrics.py` | `scripts/evaluate_metrics.py` | `a32e8b2f4aac2de1093ad5e0a14a8d4424d0bcf1f647812780870f763c446291` |
| `research_scripts` | `analyze_results.py` | `scripts/analyze_results.py` | `768256600aa18b71134a0191715e4130c879f4df61a1986ac7edae57c4b7b90f` |
| `research_scripts` | `run_ablation.py` | `scripts/run_ablation.py` | `6bc6214d1bf39f1d7e895f430d0a332b90fbd1c2f216663d336481bca06c1dad` |
| `research_scripts` | `run_evaluation.py` | `scripts/run_evaluation.py` | `2446811c495ec943c856439ee9d6f74e103e002243f223ee96cbeffb374c060d` |
| `research_scripts` | `validate_production_readiness.py` | `scripts/validate_production_readiness.py` | `64087b559d414639b13cabec7acbd1c9e9fc70a7e541bd9027116f6d4b4c1194` |
| `dependencies` | `backend_requirements.txt` | `backend/requirements.txt` | `99721287c25c9f558851465a8f9f8009bc633c46d2efa669c52c7f82353f2716` |
| `dependencies` | `frontend_package.json` | `frontend/package.json` | `c8ac8691d4788849eaf55d155a92da526611ffea50b8e247f05762cca9f2284e` |
| `dependencies` | `frontend_package_lock.json` | `frontend/package-lock.json` | `8ab4b263f3e774da2b07242a6519c31241c701f7b87fc789a9d5492cddbd8107` |

---

## 4. Thông Tin Môi Trường Thực Thi (Clean-Room Environment)

| Thành phần môi trường | Phiên bản thực tế | Ghi chú |
| :--- | :--- | :--- |
| **Python** | `3.13.9` | Môi trường backend virtualenv |
| **Node.js** | `v24.14.0` | Môi trường frontend Next.js |
| **NPM** | `11.9.0` | Quản lý gói frontend |
| **.NET SDK** | `10.0.400` | Trình biên dịch/thực thi C# |
| **Hệ điều hành (OS)** | `Windows 11 (Build 10.0.26200)` | Môi trường máy trạm Windows |

---

## 5. Cấu Hình Hệ Thống Nghiên Cứu & Mô Hình (Research Identifiers)

- **Tên Provider cấu hình:** `mock`
- **Mã mô hình yêu cầu (Requested Model Identifier):** `mock-tutor-v1`
- **Trạng thái Mock Mode:** `True` (Bộ sinh tĩnh mô phỏng harness nội bộ)
- **Cơ chế Fallback:** `Chế độ mô phỏng kiểm thử độc lập (Offline Mock Simulation Harness)`

### Danh sách 4 hệ thống đánh giá:

| Mã hệ thống | Tên hệ thống | Phiên bản Prompt | Nhiệt độ | Max Tokens | Chẩn đoán cấu trúc | Gợi ý tăng dần | Bối cảnh học viên |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **A** | Baseline A: Direct LLM Debugging Prompt | `v1.0-direct-debug` | 0.7 | 1024 | False | False | False |
| **B** | Baseline B: Generic Tutor Prompt | `v1.0-generic-tutor` | 0.7 | 1024 | False | False | False |
| **C** | Proposed C: Structured Diagnosis + Progressive Hints | `v1.0-structured-progressive` | 0.2 | 1024 | True | True | False |
| **D** | Proposed D: Structured Diagnosis + Progressive Hints + Student Context | `v1.0-contextual-adaptive` | 0.2 | 1024 | True | True | True |

---

## 6. Cam Kết Liêm Chính Khoa Học & Bảo Mật (Audit Attestation)

> [!IMPORTANT]

> 1. **Bảo mật tuyệt đối:** Bản ghi kiểm toán này không in hoặc lưu trữ bất kỳ API key, token bí mật hay cấu hình riêng tư nào.

> 2. **Bảo toàn tập Test:** Kiểm toán viên xác nhận KHÔNG thực hiện bất kỳ lệnh gọi LLM mới nào đối với tập frozen test split.

> 3. **Bảo toàn hành vi mã nguồn:** Không có bất kỳ logic nghiệp vụ hoặc tham số thực nghiệm nào bị thay đổi trong quá trình thiết lập baseline.
