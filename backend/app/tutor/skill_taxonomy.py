"""
C# OOP Beginner Skill Taxonomy (APT-017).

Hệ thống phân loại kỹ năng lập trình hướng đối tượng C# dành cho người mới bắt đầu (V1).
Đảm bảo:
1. 16 kỹ năng tối thiểu chuẩn hóa với stable code, tên tiếng Việt, mô tả, prerequisites, difficulty và taxonomy_version="v1".
2. Ngăn chặn LLM tùy tiện tạo ra các mã kỹ năng tùy ý trong database.
3. Ánh xạ mọi chẩn đoán được hỗ trợ (Every supported diagnosis) sang các kỹ năng đã biết.
"""

from dataclasses import dataclass, field
import logging
from typing import Any, Optional

from app.schemas.tutor_schema import DiagnosisCategory

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Skill:
    """Mô hình đại diện cho một kỹ năng chuẩn hóa trong Taxonomy."""
    code: str
    name: str
    description: str
    prerequisites: list[str]
    difficulty: int  # 1 (dễ nhất) đến 5 (nâng cao)
    taxonomy_version: str = "v1"


# 1. Tập hợp 16 kỹ năng tối thiểu chuẩn hóa của phiên bản V1
CSHARP_OOP_SKILLS_V1: dict[str, Skill] = {
    "csharp.class_object": Skill(
        code="csharp.class_object",
        name="Lớp và Đối tượng",
        description="Khái niệm khuôn mẫu lớp (class) và khởi tạo thực thể cụ thể (object) với toán tử new.",
        prerequisites=[],
        difficulty=1,
        taxonomy_version="v1",
    ),
    "csharp.field": Skill(
        code="csharp.field",
        name="Biến trường (Field)",
        description="Khai báo biến thành viên bên trong lớp để lưu giữ trạng thái dữ liệu của đối tượng.",
        prerequisites=["csharp.class_object"],
        difficulty=1,
        taxonomy_version="v1",
    ),
    "csharp.property": Skill(
        code="csharp.property",
        name="Thuộc tính (Property)",
        description="Cơ chế đóng gói truy cập và cập nhật trạng thái của trường thông qua getter và setter.",
        prerequisites=["csharp.class_object", "csharp.field"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.getter": Skill(
        code="csharp.getter",
        name="Bộ đọc thuộc tính (Getter)",
        description="Khối mã get trả về giá trị của thuộc tính, sử dụng biến trường lưu trữ (backing field) an toàn.",
        prerequisites=["csharp.property"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.setter": Skill(
        code="csharp.setter",
        name="Bộ gán thuộc tính (Setter)",
        description="Khối mã set gán dữ liệu cho thuộc tính thông qua từ khóa ngầm định value.",
        prerequisites=["csharp.property"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.parameter": Skill(
        code="csharp.parameter",
        name="Tham số (Parameter)",
        description="Khai báo và truyền đối số đầu vào cho hàm khởi tạo hoặc phương thức.",
        prerequisites=["csharp.class_object"],
        difficulty=1,
        taxonomy_version="v1",
    ),
    "csharp.this": Skill(
        code="csharp.this",
        name="Từ khóa this",
        description="Tham chiếu đại diện cho chính thực thể đối tượng hiện tại, dùng để phân biệt biến trường và tham số trùng tên.",
        prerequisites=["csharp.field", "csharp.parameter"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.constructor": Skill(
        code="csharp.constructor",
        name="Hàm khởi tạo (Constructor)",
        description="Phương thức đặc biệt cùng tên lớp được gọi khi tạo đối tượng để thiết lập trạng thái ban đầu.",
        prerequisites=["csharp.class_object", "csharp.field", "csharp.parameter"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.method": Skill(
        code="csharp.method",
        name="Phương thức (Method)",
        description="Hành vi và hàm xử lý nghiệp vụ của lớp và đối tượng.",
        prerequisites=["csharp.class_object", "csharp.parameter"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.encapsulation": Skill(
        code="csharp.encapsulation",
        name="Tính đóng gói (Encapsulation)",
        description="Ẩn giấu chi tiết cài đặt và bảo vệ trạng thái nội tại bằng các bộ chỉ định truy cập private và public.",
        prerequisites=["csharp.field", "csharp.property"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.validation": Skill(
        code="csharp.validation",
        name="Kiểm tra dữ liệu (Validation)",
        description="Ràng buộc kiểm tra tính hợp lệ của dữ liệu trước khi gán trong setter hoặc constructor.",
        prerequisites=["csharp.setter"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.instance": Skill(
        code="csharp.instance",
        name="Thành phần thực thể (Instance)",
        description="Các thành viên (biến, phương thức) gắn liền với từng đối tượng cụ thể và truy xuất qua biến thực thể.",
        prerequisites=["csharp.class_object"],
        difficulty=2,
        taxonomy_version="v1",
    ),
    "csharp.static": Skill(
        code="csharp.static",
        name="Thành phần tĩnh (Static)",
        description="Các thành viên gắn liền với cấp độ lớp thay vì từng thực thể đối tượng, phân biệt với instance.",
        prerequisites=["csharp.class_object", "csharp.instance"],
        difficulty=3,
        taxonomy_version="v1",
    ),
    "csharp.inheritance": Skill(
        code="csharp.inheritance",
        name="Tính kế thừa (Inheritance)",
        description="Xây dựng lớp con dẫn xuất từ lớp cha cơ sở để tái sử dụng mã nguồn và biểu diễn quan hệ 'is-a'.",
        prerequisites=["csharp.class_object"],
        difficulty=3,
        taxonomy_version="v1",
    ),
    "csharp.override": Skill(
        code="csharp.override",
        name="Ghi đè phương thức (Override)",
        description="Định nghĩa lại phương thức của lớp cha ở lớp con bằng từ khóa override kết hợp virtual.",
        prerequisites=["csharp.inheritance", "csharp.method"],
        difficulty=3,
        taxonomy_version="v1",
    ),
    "csharp.polymorphism": Skill(
        code="csharp.polymorphism",
        name="Tính đa hình (Polymorphism)",
        description="Khả năng các đối tượng thuộc các lớp khác nhau phản ứng phù hợp với cùng một lời gọi phương thức.",
        prerequisites=["csharp.inheritance", "csharp.override"],
        difficulty=4,
        taxonomy_version="v1",
    ),
}

# 2. Bảng từ đồng nghĩa / alias ánh xạ các chuỗi tự do từ LLM hoặc heuristics về stable code
SKILL_ALIASES: dict[str, str] = {
    # class_object
    "class": "csharp.class_object",
    "classes": "csharp.class_object",
    "object": "csharp.class_object",
    "objects": "csharp.class_object",
    "class_definition": "csharp.class_object",
    "class_object": "csharp.class_object",
    "csharp_syntax_basics": "csharp.class_object",
    "class_structure": "csharp.class_object",
    "syntax_correctness": "csharp.class_object",
    # field
    "field": "csharp.field",
    "fields": "csharp.field",
    "backing_field": "csharp.field",
    "backing_fields": "csharp.field",
    "member_variable": "csharp.field",
    # property
    "property": "csharp.property",
    "properties": "csharp.property",
    "csharp_properties": "csharp.property",
    "auto_property": "csharp.property",
    "property_accessors": "csharp.property",
    # getter
    "getter": "csharp.getter",
    "get_accessor": "csharp.getter",
    "property_getter": "csharp.getter",
    "recursion": "csharp.getter",
    # setter
    "setter": "csharp.setter",
    "set_accessor": "csharp.setter",
    "property_setter": "csharp.setter",
    # constructor
    "constructor": "csharp.constructor",
    "constructors": "csharp.constructor",
    "csharp_constructor": "csharp.constructor",
    "class_constructor": "csharp.constructor",
    # this
    "this": "csharp.this",
    "this_keyword": "csharp.this",
    "variable_shadowing": "csharp.this",
    "shadowing": "csharp.this",
    # parameter
    "parameter": "csharp.parameter",
    "parameters": "csharp.parameter",
    "argument": "csharp.parameter",
    # method
    "method": "csharp.method",
    "methods": "csharp.method",
    "function": "csharp.method",
    "member_function": "csharp.method",
    # encapsulation
    "encapsulation": "csharp.encapsulation",
    "access_modifier": "csharp.encapsulation",
    "access_modifiers": "csharp.encapsulation",
    "data_hiding": "csharp.encapsulation",
    "information_hiding": "csharp.encapsulation",
    # validation
    "validation": "csharp.validation",
    "data_validation": "csharp.validation",
    "setter_validation": "csharp.validation",
    "input_validation": "csharp.validation",
    # static
    "static": "csharp.static",
    "static_members": "csharp.static",
    "static_method": "csharp.static",
    "static_class": "csharp.static",
    # instance
    "instance": "csharp.instance",
    "instance_members": "csharp.instance",
    "oop_state_management": "csharp.instance",
    # inheritance
    "inheritance": "csharp.inheritance",
    "base_class": "csharp.inheritance",
    "derived_class": "csharp.inheritance",
    "subclass": "csharp.inheritance",
    # override
    "override": "csharp.override",
    "virtual": "csharp.override",
    "method_overriding": "csharp.override",
    # polymorphism
    "polymorphism": "csharp.polymorphism",
    "dynamic_binding": "csharp.polymorphism",
}

# 3. Bảng ánh xạ từ chẩn đoán (issue_type và category) sang danh sách stable skill codes
# Đảm bảo Acceptance: Every supported diagnosis maps to known skills
DIAGNOSIS_ISSUE_TO_SKILLS: dict[str, list[str]] = {
    # compile errors
    "syntax_error": ["csharp.class_object"],
    "type_mismatch": ["csharp.field", "csharp.property"],
    "missing_semicolon": ["csharp.class_object"],
    "unassigned_variable": ["csharp.field", "csharp.constructor"],
    "missing_member": ["csharp.class_object", "csharp.method"],
    "inaccessible_member": ["csharp.encapsulation"],
    "invalid_return_type": ["csharp.method", "csharp.getter"],
    "missing_return_statement": ["csharp.method", "csharp.getter"],
    "missing_closing_brace": ["csharp.class_object"],
    # runtime errors
    "recursive_property_accessor": ["csharp.property", "csharp.getter", "csharp.field"],
    "null_reference_risk": ["csharp.class_object", "csharp.constructor"],
    "index_out_of_range": ["csharp.method"],
    "divide_by_zero": ["csharp.method", "csharp.validation"],
    "invalid_cast": ["csharp.inheritance", "csharp.polymorphism"],
    "stack_overflow_risk": ["csharp.getter", "csharp.method"],
    # logic errors
    "parameter_field_shadowing": ["csharp.constructor", "csharp.this", "csharp.parameter", "csharp.field"],
    "invalid_setter_validation": ["csharp.setter", "csharp.validation", "csharp.encapsulation"],
    "incorrect_calculation": ["csharp.method"],
    "off_by_one": ["csharp.method"],
    "inverted_condition": ["csharp.validation", "csharp.method"],
    "unreachable_code": ["csharp.method"],
    "state_not_updated": ["csharp.field", "csharp.setter"],
    "semantic_error": ["csharp.class_object"],
    "logical_error": ["csharp.class_object", "csharp.method"],
    # conceptual misuse
    "static_instance_confusion": ["csharp.static", "csharp.instance", "csharp.class_object"],
    "encapsulation_bypass": ["csharp.encapsulation", "csharp.field", "csharp.property"],
    "constructor_return_type": ["csharp.constructor", "csharp.method"],
    "improper_inheritance": ["csharp.inheritance", "csharp.class_object"],
    "overload_override_confusion": ["csharp.override", "csharp.polymorphism", "csharp.method"],
    "reference_vs_value_confusion": ["csharp.class_object", "csharp.field"],
    # requirement violation
    "missing_required_member": ["csharp.class_object", "csharp.property"],
    "incorrect_signature": ["csharp.method", "csharp.parameter"],
    "incorrect_access_modifier": ["csharp.encapsulation"],
    "missing_validation_requirement": ["csharp.validation", "csharp.setter"],
    "unmet_specification": ["csharp.class_object"],
    # no bug
    "no_issue_detected": ["csharp.class_object"],
    "correct_implementation": ["csharp.class_object"],
    # insufficient context
    "incomplete_code": ["csharp.class_object"],
    "missing_class_body": ["csharp.class_object"],
    "empty_submission": ["csharp.class_object"],
    # unknown
    "unclassified_issue": ["csharp.class_object"],
}

CATEGORY_DEFAULT_SKILLS: dict[DiagnosisCategory, list[str]] = {
    DiagnosisCategory.COMPILE_ERROR: ["csharp.class_object"],
    DiagnosisCategory.RUNTIME_ERROR: ["csharp.property", "csharp.getter"],
    DiagnosisCategory.LOGIC_ERROR: ["csharp.constructor", "csharp.this"],
    DiagnosisCategory.CONCEPTUAL_MISUSE: ["csharp.encapsulation", "csharp.class_object"],
    DiagnosisCategory.REQUIREMENT_VIOLATION: ["csharp.class_object", "csharp.property"],
    DiagnosisCategory.NO_BUG: ["csharp.class_object"],
    DiagnosisCategory.INSUFFICIENT_CONTEXT: ["csharp.class_object"],
    DiagnosisCategory.UNKNOWN: ["csharp.class_object"],
}


class SkillTaxonomy:
    """Hệ thống điều phối truy vấn và chuẩn hóa Taxonomy kỹ năng C# OOP."""

    @classmethod
    def get_skill(cls, code: str) -> Optional[Skill]:
        """Lấy thông tin một kỹ năng dựa trên stable code."""
        normalized = cls.map_knowledge_component(code)
        if normalized:
            return CSHARP_OOP_SKILLS_V1.get(normalized)
        return None

    @classmethod
    def get_skill_display_name(cls, code: str) -> str:
        """Lấy tên hiển thị tiếng Việt của kỹ năng, fallback về code nếu không xác định."""
        skill = cls.get_skill(code)
        return skill.name if skill else code

    @classmethod
    def list_skills(
        cls,
        *,
        difficulty: Optional[int] = None,
        taxonomy_version: Optional[str] = None,
    ) -> list[Skill]:
        """Trả về danh sách kỹ năng, có hỗ trợ lọc theo difficulty hoặc taxonomy_version."""
        skills = list(CSHARP_OOP_SKILLS_V1.values())
        if difficulty is not None:
            skills = [s for s in skills if s.difficulty == difficulty]
        if taxonomy_version is not None:
            skills = [s for s in skills if s.taxonomy_version == taxonomy_version]
        return skills

    @classmethod
    def validate_taxonomy(cls) -> bool:
        """
        Kiểm tra tính toàn vẹn của Taxonomy:
        1. Không có mã trùng lặp (đã đảm bảo bởi dict key).
        2. Mọi prerequisite đều phải tồn tại trong taxonomy.
        3. Độ khó (difficulty) phải nằm trong đoạn [1, 5].
        4. taxonomy_version phải là 'v1'.
        """
        all_codes = set(CSHARP_OOP_SKILLS_V1.keys())

        for code, skill in CSHARP_OOP_SKILLS_V1.items():
            if skill.code != code:
                raise ValueError(f"Skill code mismatch: key='{code}' != skill.code='{skill.code}'")

            if not (1 <= skill.difficulty <= 5):
                raise ValueError(f"Skill '{code}' có độ khó không hợp lệ: {skill.difficulty} (yêu cầu 1-5)")

            if skill.taxonomy_version != "v1":
                raise ValueError(f"Skill '{code}' có phiên bản không phải 'v1': {skill.taxonomy_version}")

            for prereq in skill.prerequisites:
                if prereq not in all_codes:
                    raise ValueError(f"Skill '{code}' chứa prerequisite không tồn tại: '{prereq}'")

        return True

    @classmethod
    def map_knowledge_component(cls, raw: str) -> Optional[str]:
        """
        Ánh xạ an toàn một chuỗi tri thức tự do về stable code chuẩn trong taxonomy.
        Loại bỏ hoàn toàn các chuỗi lạ do LLM bịa đặt không nằm trong từ điển.
        """
        if not raw or not isinstance(raw, str):
            return None

        cleaned = raw.strip().lower()

        # Nếu đã là mã chuẩn
        if cleaned in CSHARP_OOP_SKILLS_V1:
            return cleaned

        # Nếu có tiền tố csharp.
        if cleaned.startswith("csharp."):
            sub = cleaned.split("csharp.", 1)[1]
            if sub in SKILL_ALIASES:
                return SKILL_ALIASES[sub]
            target = f"csharp.{sub}"
            if target in CSHARP_OOP_SKILLS_V1:
                return target

        # Tra trong alias dictionary
        if cleaned in SKILL_ALIASES:
            return SKILL_ALIASES[cleaned]

        cleaned_norm = cleaned.replace(" ", "_").replace("-", "_")
        if cleaned_norm in SKILL_ALIASES:
            return SKILL_ALIASES[cleaned_norm]

        return None

    @classmethod
    def map_knowledge_components(cls, raw_list: list[str]) -> list[str]:
        """
        Chuẩn hóa danh sách chuỗi knowledge components từ LLM:
        - Chuyển về stable codes.
        - Khử trùng lặp.
        - Lọc bỏ các chuỗi hallucinated của LLM.
        """
        if not raw_list:
            return []

        resolved: list[str] = []
        for item in raw_list:
            mapped = cls.map_knowledge_component(item)
            if mapped and mapped not in resolved:
                resolved.append(mapped)

        return resolved

    @classmethod
    def map_diagnosis_to_skills(
        cls,
        category: DiagnosisCategory,
        issue_type: str,
        raw_kc: Optional[list[str]] = None,
    ) -> list[str]:
        """
        Đảm bảo 100% mọi chẩn đoán được hỗ trợ đều ánh xạ thành công tới các kỹ năng đã biết.
        """
        mapped: list[str] = []

        # 1. Thử map từ danh sách raw knowledge components nếu có
        if raw_kc:
            mapped.extend(cls.map_knowledge_components(raw_kc))

        # 2. Thử map từ issue_type cụ thể
        clean_issue = issue_type.strip().lower() if issue_type else ""
        if clean_issue in DIAGNOSIS_ISSUE_TO_SKILLS:
            for code in DIAGNOSIS_ISSUE_TO_SKILLS[clean_issue]:
                if code not in mapped:
                    mapped.append(code)

        # 3. Fallback: Nếu vẫn chưa có kỹ năng nào, sử dụng mặc định theo DiagnosisCategory
        if not mapped:
            default_skills = CATEGORY_DEFAULT_SKILLS.get(category, ["csharp.class_object"])
            for code in default_skills:
                if code not in mapped:
                    mapped.append(code)

        return mapped
