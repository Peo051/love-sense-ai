# AUDIT BASELINE: Điểm Bắt Đầu Kiểm Toán Độc Lập

**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Nhánh kiểm toán:** `audit/evaluation-integrity-v1`  
**Thời gian tạo:** 2026-09-06T18:05:00+07:00  
**Vai trò:** Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  

---

## 1. Trạng Thái Mã Nguồn & Git Baseline

| Thuộc tính | Giá trị / Hash | Ghi chú |
| :--- | :--- | :--- |
| **Current Git Branch** | `audit/evaluation-integrity-v1` | Nhánh kiểm toán độc lập |
| **Current Commit SHA** | `3035e069d26892a010276993bdc452c9a458f45c` | Khởi tạo từ release v1.0 |
| **Release Tag `codesense-research-v1.0` Commit** | `3035e069d26892a010276993bdc452c9a458f45c` | Điểm neo chuẩn phát hành |
| **Trạng thái đối chiếu Commit** | **KHỚP TUYỆT ĐỐI** (`True`) | Không có sửa đổi trái phép trước kiểm toán |

---

## 2. Hash Tệp Dữ Liệu & Test Split

| Tệp / Phân vùng | Số lượng mẫu | SHA-256 Checksum |
| :--- | :---: | :--- |
| **Tập dữ liệu gốc (`vietcsharptutor_600.jsonl`)** | 600 | `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed` |
| **Phân vùng `dev`** | 360 | `4883098109f85fa42e1e7e874c2f11ddc51f59987e931dcda388ce862a98a52b` |
| **Phân vùng `validation`** | 120 | `d9b3ad1339228aa4c47c9444def07ab013cef8498bcc244afbe24a7218b3349a` |
| **Phân vùng `test` (Frozen Test Split)** | 120 | `65aa09f289f3db70846730b3b73a75395b61b50a2b33412ddd2a7c6aa6a39544` |

---

## 3. Hash Tệp Cấu Hình, Pipeline Đánh Giá & Lockfiles

| Tệp thành phần | Đường dẫn | SHA-256 Checksum |
| :--- | :--- | :--- |
| `runner.py` | `backend/app/evaluation/runner.py` | `a1ffa68f5fa3d38fa67d2b8b5c52afcd227288da54c0c63b4bcea60a1474e428` |
| `prompts.py` | `backend/app/evaluation/prompts.py` | `bf658267576906fec5a423a0b7f62c774a8e12a34955cfedb0ad29d3b3dc741b` |
| `metrics.py` | `backend/app/evaluation/metrics.py` | `104b732ca17fab64ec4251156209bf1e01f1ed3dcd96d644f97a191caedbaeb1` |
| `ablation.py` | `backend/app/evaluation/ablation.py` | `fb824572145de69abcf03909914b7413f1399017a74e9a68d1a247f093e5e740` |
| `requirements.txt` | `backend/requirements.txt` | `99721287c25c9f558851465a8f9f8009bc633c46d2efa669c52c7f82353f2716` |
| `package.json` | `frontend/package.json` | `c8ac8691d4788849eaf55d155a92da526611ffea50b8e247f05762cca9f2284e` |
| `package-lock.json` | `frontend/package-lock.json` | `8ab4b263f3e774da2b07242a6519c31241c701f7b87fc789a9d5492cddbd8107` |
| `evaluation_results.json` | `results/evaluation_results.json` | `6b2bef763100ec6bc789a6ddc9246af329d2e9f5200ef7211a741e39d624991b` |
| `ablation_results.json` | `results/ablation_results.json` | `415e5d3dae7dcad2e81b32e78f16f5e9dec425c98aaa4012f92698379a7f75e4` |
| `ANALYSIS_SUMMARY.md` | `results/ANALYSIS_SUMMARY.md` | `a5c5c81a2b89990afde1296bebdbb0f1f502c06272b8b911aafa6237c3f268e7` |
| `statistical_tests.json` | `results/statistical_tests.json` | `1faaa9b32825aa57214beb6c9a0c06867bc4c46335d18a5b22cc5ffe68274313` |
| `error_analysis.json` | `results/error_analysis.json` | `b3aaccee7546e3a32026770c79d4feabda9a20806900c94dd8626ee297c1102b` |
| `overall_comparison.csv` | `results/overall_comparison.csv` | `50ee4ae0681fcf98d558ec2356f75a76083735a262031e9067fb62c077506a5b` |

---

## 4. Cấu Hình Hệ Thống Đánh Giá (Systems Under Audit)

```json
{
  "A": {
    "name": "Baseline A: Direct LLM Debugging Prompt",
    "model": "mock-tutor-v1",
    "provider": "mock",
    "temperature": 0.7,
    "max_output_tokens": 1024,
    "prompt_version": "v1.0-direct-debug",
    "use_student_context": false,
    "progressive_hints": false,
    "structured_diagnosis": false
  },
  "B": {
    "name": "Baseline B: Generic Tutor Prompt",
    "model": "mock-tutor-v1",
    "provider": "mock",
    "temperature": 0.7,
    "max_output_tokens": 1024,
    "prompt_version": "v1.0-generic-tutor",
    "use_student_context": false,
    "progressive_hints": false,
    "structured_diagnosis": false
  },
  "C": {
    "name": "Proposed C: Structured Diagnosis + Progressive Hints",
    "model": "mock-tutor-v1",
    "provider": "mock",
    "temperature": 0.2,
    "max_output_tokens": 1024,
    "prompt_version": "v1.0-structured-progressive",
    "use_student_context": false,
    "progressive_hints": true,
    "structured_diagnosis": true
  },
  "D": {
    "name": "Proposed D: Structured Diagnosis + Progressive Hints + Student Context",
    "model": "mock-tutor-v1",
    "provider": "mock",
    "temperature": 0.2,
    "max_output_tokens": 1024,
    "prompt_version": "v1.0-contextual-adaptive",
    "use_student_context": true,
    "progressive_hints": true,
    "structured_diagnosis": true
  }
}
```

---

## 5. Danh Sách Run Manifests & Artifacts Đóng Băng

Các artifacts của đợt chạy đóng băng ngày 2026-09-06:
- **Baseline A (Test):** `runs/run_A_test_20260906_103703`
- **Baseline B (Test):** `runs/run_B_test_20260906_103703`
- **Proposed C (Test):** `runs/run_C_test_20260906_103703`
- **Proposed D (Test):** `runs/run_D_test_20260906_103703`
- **Ablation Studies (Test):** `runs/ablation_*_test_20260906_103703`
- **Báo cáo kết quả tổng hợp:** `results/ANALYSIS_SUMMARY.md`

> **Xác nhận bảo mật:** Kiểm toán viên xác nhận không có bất kỳ API key, bí mật chứng thực hay thông tin nhạy cảm nào được in ra hoặc ghi nhận trong baseline này.
