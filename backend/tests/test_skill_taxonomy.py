"""
Unit & Integration Tests for C# OOP Beginner Skill Taxonomy (APT-017).

Verifies:
1. Minimum 16 canonical skills present with Vietnamese names, descriptions, difficulty, and v1 version.
2. No duplicate skill codes and prerequisites refer only to valid skills (no dead references, no cycles).
3. LLM cannot create arbitrary skill names: unknown strings are filtered/sanitized.
4. Every supported diagnosis (all TAXONOMY_ISSUE_TYPES) maps to known canonical skills (Acceptance Criteria).
5. DiagnosisSubsystem and TutorOutputValidator enforce canonical skill codes.
"""

import json
import pytest

from app.schemas.tutor_schema import DiagnosisCategory, IssueSeverity
from app.tutor.diagnosis import DiagnosisSubsystem
from app.tutor.skill_taxonomy import (
    CSHARP_OOP_SKILLS_V1,
    DIAGNOSIS_ISSUE_TO_SKILLS,
    SKILL_ALIASES,
    Skill,
    SkillTaxonomy,
)
from app.tutor.taxonomy import TAXONOMY_ISSUE_TYPES
from app.tutor.validator import TutorOutputValidator


MINIMUM_REQUIRED_SKILLS = [
    "csharp.class_object",
    "csharp.field",
    "csharp.property",
    "csharp.getter",
    "csharp.setter",
    "csharp.constructor",
    "csharp.this",
    "csharp.parameter",
    "csharp.method",
    "csharp.encapsulation",
    "csharp.validation",
    "csharp.static",
    "csharp.instance",
    "csharp.inheritance",
    "csharp.override",
    "csharp.polymorphism",
]


class TestSkillTaxonomyIntegrity:
    """Kiểm tra tính toàn vẹn của Skill Taxonomy V1."""

    def test_all_sixteen_minimum_skills_present(self):
        """Đảm bảo tối thiểu 16 kỹ năng cốt lõi được định nghĩa trong CSHARP_OOP_SKILLS_V1."""
        for skill_code in MINIMUM_REQUIRED_SKILLS:
            assert skill_code in CSHARP_OOP_SKILLS_V1, f"Thiếu kỹ năng bắt buộc: {skill_code}"

    def test_no_duplicate_skill_codes(self):
        """Xác nhận không có mã kỹ năng bị trùng lặp."""
        codes = [s.code for s in CSHARP_OOP_SKILLS_V1.values()]
        assert len(codes) == len(set(codes))

    def test_skill_attributes_validity(self):
        """Mỗi kỹ năng phải có đủ: code, tên tiếng Việt, mô tả, prerequisites, difficulty (1-5), version (v1)."""
        for code, skill in CSHARP_OOP_SKILLS_V1.items():
            assert skill.code == code
            assert skill.name and isinstance(skill.name, str)
            assert skill.description and len(skill.description) > 10
            assert isinstance(skill.prerequisites, list)
            assert 1 <= skill.difficulty <= 5
            assert skill.taxonomy_version == "v1"

    def test_prerequisites_refer_to_valid_skills(self):
        """Mọi kỹ năng tiên quyết (prerequisite) đều phải tồn tại trong CSHARP_OOP_SKILLS_V1."""
        for code, skill in CSHARP_OOP_SKILLS_V1.items():
            for prereq in skill.prerequisites:
                assert prereq in CSHARP_OOP_SKILLS_V1, (
                    f"Kỹ năng '{code}' tham chiếu prerequisite không tồn tại: '{prereq}'"
                )
                assert prereq != code, f"Kỹ năng '{code}' không được tự phụ thuộc vào chính mình"

    def test_no_circular_dependencies_in_prerequisites(self):
        """Đảm bảo đồ thị phụ thuộc prerequisites không bị chu trình (cycle)."""
        visited = set()
        rec_stack = set()

        def has_cycle(skill_code: str) -> bool:
            visited.add(skill_code)
            rec_stack.add(skill_code)
            skill = CSHARP_OOP_SKILLS_V1.get(skill_code)
            if skill:
                for prereq in skill.prerequisites:
                    if prereq not in visited:
                        if has_cycle(prereq):
                            return True
                    elif prereq in rec_stack:
                        return True
            rec_stack.remove(skill_code)
            return False

        for code in CSHARP_OOP_SKILLS_V1:
            if code not in visited:
                assert not has_cycle(code), f"Phát hiện chu trình phụ thuộc bắt đầu từ '{code}'"

    def test_validate_taxonomy_helper(self):
        """Hàm helper validate_taxonomy() của SkillTaxonomy phải trả về True và không có lỗi."""
        assert SkillTaxonomy.validate_taxonomy() is True


class TestSkillLookupAndAliases:
    """Kiểm tra tra cứu kỹ năng và ánh xạ bí danh (aliases)."""

    def test_get_skill_success_and_fail(self):
        skill = SkillTaxonomy.get_skill("csharp.class_object")
        assert skill is not None
        assert skill.name == "Lớp và Đối tượng"

        # Tra cứu mã không tồn tại
        assert SkillTaxonomy.get_skill("csharp.non_existent") is None
        assert SkillTaxonomy.get_skill("") is None
        assert SkillTaxonomy.get_skill(None) is None

    def test_list_skills_filtering(self):
        v1_skills = SkillTaxonomy.list_skills(taxonomy_version="v1")
        assert len(v1_skills) == len(CSHARP_OOP_SKILLS_V1)

        diff1_skills = SkillTaxonomy.list_skills(difficulty=1)
        assert len(diff1_skills) > 0
        assert all(s.difficulty == 1 for s in diff1_skills)

    def test_alias_mapping(self):
        """Ánh xạ các chuỗi alias thường gặp về mã chuẩn."""
        assert SkillTaxonomy.map_knowledge_component("class") == "csharp.class_object"
        assert SkillTaxonomy.map_knowledge_component("encapsulation") == "csharp.encapsulation"
        assert SkillTaxonomy.map_knowledge_component("this") == "csharp.this"
        assert SkillTaxonomy.map_knowledge_component("getter") == "csharp.getter"
        assert SkillTaxonomy.map_knowledge_component("setter") == "csharp.setter"
        assert SkillTaxonomy.map_knowledge_component("csharp.class_object") == "csharp.class_object"


class TestArbitrarySkillNameSanitization:
    """Kiểm tra việc ngăn chặn LLM bịa đặt tên kỹ năng tùy tiện."""

    def test_hallucinated_skill_names_are_dropped(self):
        """Các chuỗi tùy tiện do LLM tự sinh không được lọt vào database hay taxonomy."""
        arbitrary_inputs = [
            "completely_made_up_skill",
            "quantum_programming_csharp",
            "python_function_def",
            "csharp.fake_feature",
            "random_nonsense_123",
            "",
            "   ",
        ]
        for item in arbitrary_inputs:
            mapped = SkillTaxonomy.map_knowledge_component(item)
            assert mapped is None, f"Chuỗi bịa đặt '{item}' không được phép map thành công"

    def test_map_knowledge_components_filters_invalid_and_preserves_valid(self):
        raw_list = [
            "completely_fake_skill",
            "class",  # alias -> csharp.class_object
            "csharp.method",  # canonical
            "another_hallucination",
            "this_keyword",  # alias -> csharp.this
        ]
        filtered = SkillTaxonomy.map_knowledge_components(raw_list)
        assert filtered == [
            "csharp.class_object",
            "csharp.method",
            "csharp.this",
        ]
        # Tất cả các phần tử đầu ra phải là mã chuẩn
        for code in filtered:
            assert code in CSHARP_OOP_SKILLS_V1


class TestEverySupportedDiagnosisMapsToKnownSkills:
    """
    Acceptance Criteria:
    'Every supported diagnosis maps to known skills.'
    Kiểm tra toàn bộ TAXONOMY_ISSUE_TYPES khớp sang kỹ năng đã biết trong taxonomy.
    """

    def test_all_taxonomy_issue_types_map_to_canonical_skills(self):
        """Tất cả 40+ issue types trong taxonomy phải map thành công sang ít nhất 1 canonical skill."""
        for category, issue_types in TAXONOMY_ISSUE_TYPES.items():
            for issue_type in issue_types:
                mapped_skills = SkillTaxonomy.map_diagnosis_to_skills(
                    category=category,
                    issue_type=issue_type,
                    raw_kc=[],
                )
                assert len(mapped_skills) >= 1, (
                    f"Chẩn đoán ({category.value}, {issue_type}) không map tới kỹ năng nào!"
                )
                for skill_code in mapped_skills:
                    assert skill_code in CSHARP_OOP_SKILLS_V1, (
                        f"Chẩn đoán ({category.value}, {issue_type}) map tới skill không tồn tại: '{skill_code}'"
                    )

    def test_fallback_when_unknown_category_and_issue(self):
        """Khi gặp category/issue hoàn toàn lạ, vẫn fallback an toàn về canonical skill."""
        mapped = SkillTaxonomy.map_diagnosis_to_skills(
            category=DiagnosisCategory.UNKNOWN,
            issue_type="completely_unknown_bug_type",
            raw_kc=[],
        )
        assert len(mapped) >= 1
        assert all(code in CSHARP_OOP_SKILLS_V1 for code in mapped)


class TestDiagnosisSubsystemIntegration:
    """Kiểm tra tích hợp SkillTaxonomy trong DiagnosisSubsystem."""

    def test_heuristic_diagnoses_return_canonical_skills(self):
        """Tất cả các heuristic detectors trả về canonical skill codes."""
        # 1. Recursive getter
        rec_code = """
        class Account {
            private decimal _balance;
            public decimal Balance {
                get { return Balance; }
            }
        }
        """
        diag_rec = DiagnosisSubsystem.diagnose(student_code=rec_code)
        assert diag_rec.issue_type == "recursive_property_accessor"
        assert len(diag_rec.knowledge_components) > 0
        for code in diag_rec.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1

        # 2. Shadowing
        shadow_code = """
        class Student {
            private string name;
            public Student(string name) {
                name = name;
            }
        }
        """
        diag_shadow = DiagnosisSubsystem.diagnose(student_code=shadow_code)
        assert diag_shadow.issue_type == "parameter_field_shadowing"
        for code in diag_shadow.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1

        # 3. Static/instance confusion
        static_code = """
        class Car {
            public static int speed;
        }
        """
        diag_static = DiagnosisSubsystem.diagnose(student_code=static_code)
        assert diag_static.issue_type == "static_instance_confusion"
        for code in diag_static.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1

        # 4. Valid code (no bug)
        clean_code = """
        class Circle {
            private double _radius;
            public Circle(double radius) {
                _radius = radius;
            }
            public double GetArea() {
                return 3.14 * _radius * _radius;
            }
        }
        """
        diag_clean = DiagnosisSubsystem.diagnose(student_code=clean_code)
        assert diag_clean.category == DiagnosisCategory.NO_BUG
        for code in diag_clean.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1

    def test_normalize_diagnosis_replaces_hallucinated_skills(self):
        """normalize_diagnosis lọc sạch các skill bịa đặt của LLM."""
        raw_dict = {
            "category": "logic_error",
            "issue_type": "parameter_field_shadowing",
            "severity": "warning",
            "confidence": 0.9,
            "knowledge_components": ["made_up_skill_1", "another_fake"],
        }
        norm = DiagnosisSubsystem.normalize_diagnosis(raw_dict)
        # Vì toàn bộ raw_kc bị loại bỏ, hàm tự động fallback về canonical skills của issue_type
        assert len(norm.knowledge_components) > 0
        for code in norm.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1


class TestTutorOutputValidatorIntegration:
    """Kiểm tra TutorOutputValidator chuẩn hóa skill codes qua SkillTaxonomy."""

    def test_validator_cleans_and_sanitizes_llm_output_skills(self):
        mock_output = json.dumps({
            "diagnosis": {
                "category": "logic_error",
                "issue_type": "parameter_field_shadowing",
                "severity": "warning",
                "confidence": 0.9,
                "evidence": {
                    "code": "name = name;",
                    "reason": "Gán vào chính nó.",
                },
                "knowledge_components": ["this", "fake_concept_xyz"],
            },
            "knowledge_components": ["constructor", "completely_invented_skill"],
            "teaching_strategy": "socratic_questioning",
            "tutor_response": "Hãy xem lại phép gán tham số.",
            "hint_level": 1,
            "solution_revealed": False,
            "next_action": "Sửa lại phép gán.",
            "prompt_version": "v1",
        })

        response = TutorOutputValidator.parse_and_validate(
            mock_output,
            student_code="class Student { public Student(string name) { name = name; } }",
        )

        # Kiểm tra diagnosis.knowledge_components
        assert "csharp.this" in response.diagnosis.knowledge_components
        assert "fake_concept_xyz" not in response.diagnosis.knowledge_components
        for code in response.diagnosis.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1

        # Kiểm tra top-level response.knowledge_components
        assert "csharp.constructor" in response.knowledge_components
        assert "completely_invented_skill" not in response.knowledge_components
        for code in response.knowledge_components:
            assert code in CSHARP_OOP_SKILLS_V1
