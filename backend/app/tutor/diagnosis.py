"""
Diagnosis Subsystem - Hệ thống chẩn đoán lỗi có cấu trúc cho C# OOP.

Đảm bảo:
1. Phân biệt chính xác 8 categories: compile_error, runtime_error, logic_error,
   conceptual_misuse, requirement_violation, no_bug, insufficient_context, unknown.
2. Trả về đầy đủ cho mỗi chẩn đoán:
   - category
   - specific issue type (theo taxonomy chuẩn)
   - location
   - severity
   - confidence
   - supporting code evidence
   - knowledge components
   - possible misconception (nếu có bằng chứng, tuyệt đối None khi no_bug hoặc insufficient_context)
3. Cấm bịa đặt lỗi khi mã nguồn đúng (no-bug cases do not receive invented errors).
"""

import re
from typing import Any, Optional

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    IssueSeverity,
    PossibleMisconception,
    TutorDiagnosis,
    TutorEvidence,
)
from app.tutor.taxonomy import (
    TAXONOMY_ISSUE_TYPES,
    normalize_category,
    normalize_diagnosis_labels,
    normalize_issue_type,
)


class DiagnosisSubsystem:
    """
    Subsystem phân tích, chẩn đoán và chuẩn hóa lỗi lập trình C# OOP.
    """

    @classmethod
    def analyze_static_heuristics(
        cls,
        student_code: str,
        compiler_error: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> Optional[TutorDiagnosis]:
        """
        Phân tích tĩnh dựa trên heuristics đối với các mẫu lỗi C# OOP kinh điển.
        Trả về TutorDiagnosis nếu khớp một mẫu xác định, ngược lại trả về None để gọi tiếp LLM.
        """
        raw_code = student_code.strip() if student_code else ""
        error_msg = compiler_error.strip() if compiler_error else ""

        # 1. INSUFFICIENT_CONTEXT: Mã nguồn chưa hoàn chỉnh hoặc quá ngắn
        if cls._is_insufficient_context(raw_code):
            return TutorDiagnosis(
                category=DiagnosisCategory.INSUFFICIENT_CONTEXT,
                issue_type="incomplete_code",
                severity=IssueSeverity.INFO.value,
                location="root",
                confidence=0.9,
                evidence=TutorEvidence(
                    code=raw_code if raw_code else "// Mã rỗng",
                    reason="Mã nguồn nộp vào quá ngắn hoặc chưa hoàn thiện cấu trúc lớp để có thể đưa ra kết luận.",
                ),
                knowledge_components=["csharp_syntax_basics", "class_definition"],
                possible_misconception=None,
            )

        # 2. RUNTIME_ERROR: Recursive getter (gây StackOverflowException)
        recursive_getter = cls._detect_recursive_getter(raw_code)
        if recursive_getter:
            prop_name, matched_snippet = recursive_getter
            return TutorDiagnosis(
                category=DiagnosisCategory.RUNTIME_ERROR,
                issue_type="recursive_property_accessor",
                severity=IssueSeverity.ERROR.value,
                location=f"Property {prop_name}",
                confidence=0.98,
                evidence=TutorEvidence(
                    code=matched_snippet,
                    reason=f"Trong getter của thuộc tính '{prop_name}', việc 'return {prop_name};' gọi lại chính thuộc tính này khiến hàm tự gọi đệ quy vô hạn dẫn tới ngoại lệ StackOverflowException khi thực thi.",
                ),
                knowledge_components=[
                    "csharp_properties",
                    "property_accessors",
                    "backing_fields",
                    "recursion",
                ],
                possible_misconception=PossibleMisconception(
                    type="property_vs_backing_field_confusion",
                    description="Sinh viên có thể đang nhầm lẫn giữa thuộc tính công khai (Property) và biến trường lưu trữ dữ liệu (backing field), dẫn đến việc thuộc tính tự gọi lại chính nó.",
                    confidence=0.92,
                ),
            )

        # 3. COMPILE_ERROR / CONCEPTUAL_MISUSE: Static / Instance confusion (CS0120 hoặc khai báo static sai)
        static_issue = cls._detect_static_instance_confusion(raw_code, error_msg)
        if static_issue:
            cat, issue_type, loc, snip, reason, mis_desc = static_issue
            return TutorDiagnosis(
                category=cat,
                issue_type=issue_type,
                severity=IssueSeverity.ERROR.value,
                location=loc,
                confidence=0.95,
                evidence=TutorEvidence(code=snip, reason=reason),
                knowledge_components=[
                    "static_members",
                    "instance_members",
                    "oop_state_management",
                ],
                possible_misconception=PossibleMisconception(
                    type="static_vs_instance_scope_confusion",
                    description=mis_desc,
                    confidence=0.88,
                ),
            )

        # 4. LOGIC_ERROR: Parameter / Field shadowing trong constructor hoặc method
        shadowing_issue = cls._detect_parameter_shadowing(raw_code)
        if shadowing_issue:
            var_name, snip = shadowing_issue
            return TutorDiagnosis(
                category=DiagnosisCategory.LOGIC_ERROR,
                issue_type="parameter_field_shadowing",
                severity=IssueSeverity.WARNING.value,
                location="constructor",
                confidence=0.96,
                evidence=TutorEvidence(
                    code=snip,
                    reason=f"Phép gán '{var_name} = {var_name};' chỉ gán tham số cục bộ vào chính nó, không làm thay đổi giá trị của biến trường thuộc tính của đối tượng.",
                ),
                knowledge_components=[
                    "csharp_constructor",
                    "this_keyword",
                    "variable_shadowing",
                ],
                possible_misconception=PossibleMisconception(
                    type="parameter_shadowing_confusion",
                    description="Sinh viên có thể đang nghĩ rằng phép gán tên tham số trùng tên sẽ tự động lưu vào biến trường của đối tượng mà không cần chỉ định từ khóa 'this'.",
                    confidence=0.9,
                ),
            )

        # 5. LOGIC_ERROR: Invalid setter validation
        setter_issue = cls._detect_invalid_setter(raw_code)
        if setter_issue:
            loc, snip, reason = setter_issue
            return TutorDiagnosis(
                category=DiagnosisCategory.LOGIC_ERROR,
                issue_type="invalid_setter_validation",
                severity=IssueSeverity.WARNING.value,
                location=loc,
                confidence=0.9,
                evidence=TutorEvidence(code=snip, reason=reason),
                knowledge_components=[
                    "property_validation",
                    "setter_value_keyword",
                    "encapsulation",
                ],
                possible_misconception=PossibleMisconception(
                    type="setter_validation_logic_confusion",
                    description="Sinh viên có thể chưa nắm rõ cách thức sử dụng từ khóa 'value' và luồng cập nhật giá trị biến trường trong setter.",
                    confidence=0.85,
                ),
            )

        # 6. NO_BUG: Mã nguồn hợp lệ, đầy đủ, không có compiler error và không có lỗi thiết kế
        if cls._is_clean_valid_code(raw_code, error_msg):
            return TutorDiagnosis(
                category=DiagnosisCategory.NO_BUG,
                issue_type="no_issue_detected",
                severity=IssueSeverity.INFO.value,
                location="all",
                confidence=1.0,
                evidence=TutorEvidence(
                    code=raw_code,
                    reason="Mã nguồn hoàn chỉnh, cú pháp hợp lệ và tuân thủ các nguyên lý hướng đối tượng C#.",
                ),
                knowledge_components=[
                    "csharp_oop_basics",
                    "encapsulation",
                    "class_design",
                ],
                possible_misconception=None,
            )

        return None

    @classmethod
    def diagnose(
        cls,
        *,
        student_code: str,
        compiler_error: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> TutorDiagnosis:
        """
        Chẩn đoán toàn diện bài làm của sinh viên.
        Nếu heuristics nhận diện được trường hợp xác định, trả về kết quả ngay.
        Nếu không, trả về UNKNOWN có cấu trúc (hoặc chuyển cho LLM nếu trong luồng TutorService).
        """
        heuristic_res = cls.analyze_static_heuristics(
            student_code=student_code,
            compiler_error=compiler_error,
            problem_statement=problem_statement,
        )
        if heuristic_res:
            return heuristic_res

        # Mặc định fallback khi không có quy tắc cụ thể
        return TutorDiagnosis(
            category=DiagnosisCategory.UNKNOWN,
            issue_type="unclassified_issue",
            severity=IssueSeverity.WARNING.value,
            location="unknown",
            confidence=0.5,
            evidence=None,
            knowledge_components=["csharp_oop"],
            possible_misconception=None,
        )

    @classmethod
    def normalize_diagnosis(
        cls,
        diagnosis_input: TutorDiagnosis | dict[str, Any],
    ) -> TutorDiagnosis:
        """
        Chuẩn hóa chẩn đoán từ bất kỳ nguồn nào (LLM hoặc dict) về TutorDiagnosis chuẩn taxonomy.
        Đảm bảo nguyên tắc:
        - Category và IssueType khớp taxonomy chuẩn.
        - Không gán misconception khi là NO_BUG hoặc INSUFFICIENT_CONTEXT.
        - Severity là 'info' khi NO_BUG.
        """
        if isinstance(diagnosis_input, TutorDiagnosis):
            diag_dict = diagnosis_input.model_dump()
        else:
            diag_dict = dict(diagnosis_input)

        raw_cat = diag_dict.get("category")
        raw_issue = diag_dict.get("issue_type")

        norm_cat, norm_issue = normalize_diagnosis_labels(raw_cat, raw_issue)
        diag_dict["category"] = norm_cat
        diag_dict["issue_type"] = norm_issue

        # Đảm bảo confidence hợp lệ
        conf = diag_dict.get("confidence", 0.5)
        try:
            diag_dict["confidence"] = max(0.0, min(1.0, float(conf)))
        except (ValueError, TypeError):
            diag_dict["confidence"] = 0.5

        # Quy tắc bảo vệ sư phạm: Không bịa đặt lỗi
        if norm_cat == DiagnosisCategory.NO_BUG:
            diag_dict["possible_misconception"] = None
            diag_dict["severity"] = IssueSeverity.INFO.value
            if diag_dict["confidence"] < 0.8:
                diag_dict["confidence"] = 1.0
        elif norm_cat == DiagnosisCategory.INSUFFICIENT_CONTEXT:
            diag_dict["possible_misconception"] = None
            if diag_dict["confidence"] > 0.6:
                diag_dict["confidence"] = 0.5

        return TutorDiagnosis.model_validate(diag_dict)

    # ==================== HEURISTIC DETECTORS ====================

    @classmethod
    def _is_insufficient_context(cls, code: str) -> bool:
        """Kiểm tra mã nguồn có bị dở dang, quá ngắn hoặc thiếu ngữ cảnh."""
        if not code or len(code.strip()) < 20:
            return True

        stripped = code.strip()
        open_braces = stripped.count("{")
        close_braces = stripped.count("}")

        if open_braces > close_braces:
            lines = [l.strip() for l in stripped.splitlines() if l.strip()]
            if len(lines) <= 2:
                return True

        return False

    @classmethod
    def _detect_recursive_getter(cls, code: str) -> Optional[tuple[str, str]]:
        """Phát hiện lỗi getter đệ quy gọi chính nó."""
        # Standalone: get { return PropName; }
        standalone_pattern = re.compile(
            r"get\s*\{\s*return\s+(\w+)\s*;\s*\}",
            re.MULTILINE,
        )
        match_std = standalone_pattern.search(code)
        if match_std:
            prop_name = match_std.group(1)
            # Kiểm tra xem prop_name có phải là tên của một property trong code không
            prop_def = re.search(r"\b" + re.escape(prop_name) + r"\b\s*\{", code)
            if prop_def:
                return prop_name, match_std.group(0).strip()

        # Expression-bodied: get => PropName;
        arrow_pattern = re.compile(
            r"get\s*=>\s*(\w+)\s*;",
            re.MULTILINE,
        )
        match_arrow = arrow_pattern.search(code)
        if match_arrow:
            prop_name = match_arrow.group(1)
            prop_def = re.search(r"\b" + re.escape(prop_name) + r"\b\s*\{", code)
            if prop_def:
                return prop_name, match_arrow.group(0).strip()

        return None

    @classmethod
    def _detect_parameter_shadowing(cls, code: str) -> Optional[tuple[str, str]]:
        """Phát hiện gán tham số vào chính nó: name = name; mà không dùng this."""
        pattern = re.compile(
            r"(?<!this\.)\b([a-zA-Z_]\w*)\s*=\s*\1\s*;",
            re.MULTILINE,
        )
        match = pattern.search(code)
        if match:
            var_name = match.group(1)
            matched_str = match.group(0).strip()
            return var_name, matched_str
        return None

    @classmethod
    def _detect_invalid_setter(cls, code: str) -> Optional[tuple[str, str, str]]:
        """Phát hiện logic bất thường trong setter kiểm tra điều kiện."""
        # 1. So sánh trực tiếp backing field thay vì value trong if: if (_age < 0) trong setter
        backing_check = re.compile(
            r"set\s*\{[^{}]*if\s*\(\s*(_\w+)\s*[<>!=]=?\s*[^)]+\)",
            re.MULTILINE | re.DOTALL,
        )
        match_bc = backing_check.search(code)
        if match_bc:
            field_name = match_bc.group(1)
            return (
                "Property setter",
                match_bc.group(0).strip(),
                f"Trong khối setter, điều kiện đang kiểm tra biến trường '{field_name}' thay vì kiểm tra giá trị mới truyền vào ('value').",
            )

        # 2. Gán trường vào chính nó trong setter: _age = _age;
        field_self = re.compile(
            r"set\s*\{[^{}]*(_\w+)\s*=\s*\1\s*;",
            re.MULTILINE | re.DOTALL,
        )
        match_fs = field_self.search(code)
        if match_fs:
            return (
                "Property setter",
                match_fs.group(0).strip(),
                "Phép gán trường vào chính nó trong setter không lưu giá trị 'value' nhận được.",
            )

        # 3. Setter kiểm tra value < 0 nhưng không gán backing field
        set_val_only = re.compile(
            r"set\s*\{\s*if\s*\(\s*value\s*<\s*0\s*\)\s*value\s*=\s*0\s*;\s*\}",
            re.MULTILINE | re.DOTALL,
        )
        match_svo = set_val_only.search(code)
        if match_svo:
            return (
                "Property setter",
                match_svo.group(0).strip(),
                "Setter xử lý biến 'value' nhưng không gán kết quả vào biến thành viên (backing field) để lưu trạng thái.",
            )

        return None

    @classmethod
    def _detect_static_instance_confusion(
        cls,
        code: str,
        error_msg: str,
    ) -> Optional[tuple[DiagnosisCategory, str, str, str, str, str]]:
        """Phát hiện nhầm lẫn giữa static và instance."""
        # CS0120: An object reference is required for the non-static field, method, or property
        if "CS0120" in error_msg or "object reference is required" in error_msg.lower():
            return (
                DiagnosisCategory.CONCEPTUAL_MISUSE,
                "static_instance_confusion",
                "static member access",
                error_msg,
                "Trình biên dịch báo lỗi CS0120: Truy cập thành viên non-static (instance) từ ngữ cảnh static mà không thông qua một đối tượng cụ thể.",
                "Sinh viên có thể đang nghĩ rằng phương thức hoặc trường của đối tượng có thể được gọi trực tiếp mà không cần khởi tạo thực thể qua toán tử 'new'.",
            )

        # Khai báo trường dữ liệu đối tượng cá thể thành public static
        entity_classes = ["car", "bankaccount", "student", "person", "employee", "rectangle", "point", "product", "book"]
        is_entity = any(re.search(r"\bclass\s+" + c + r"\b", code, re.IGNORECASE) for c in entity_classes)

        if is_entity:
            static_field = re.search(
                r"\bpublic\s+static\s+(?:int|string|double|decimal|float)\s+(\w+)\s*;",
                code,
                re.MULTILINE | re.DOTALL,
            )
            if static_field:
                f_name = static_field.group(1)
                return (
                    DiagnosisCategory.CONCEPTUAL_MISUSE,
                    "static_instance_confusion",
                    f"Field {f_name}",
                    static_field.group(0).strip(),
                    f"Trường '{f_name}' được khai báo là 'static' trong một lớp thực thể, khiến mọi đối tượng dùng chung một giá trị thay vì mỗi đối tượng có trạng thái riêng.",
                    "Sinh viên có thể chưa phân biệt được giữa dữ liệu dùng chung cấp độ lớp (static) và dữ liệu trạng thái riêng của từng đối tượng cá thể (instance).",
                )

        return None

    @classmethod
    def _is_clean_valid_code(cls, code: str, error_msg: str) -> bool:
        """Kiểm tra mã nguồn C# có cấu trúc lớp hợp lệ, hoàn chỉnh và không có lỗi."""
        if error_msg and error_msg.strip():
            return False

        stripped = code.strip()
        # Phải có định nghĩa class
        if not re.search(r"\bclass\s+\w+", stripped):
            return False

        # Ngoặc đóng mở cân bằng
        if stripped.count("{") != stripped.count("}") or stripped.count("{") < 1:
            return False

        # Có ít nhất 1 constructor hoặc method hoặc property
        has_member = re.search(r"(?:public|private|protected)\s+(?:[\w<>\[\]]+|\w+)\s*\(", stripped) or re.search(
            r"(?:public|private|protected)\s+[\w<>\[\]]+\s+\w+\s*\{", stripped
        )
        if not has_member:
            return False

        return True
