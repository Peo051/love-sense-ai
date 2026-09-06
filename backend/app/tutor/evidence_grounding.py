"""
Evidence Grounding Validator - Module xác thực bằng chứng mã nguồn cho AI Tutor.

Nhiệm vụ:
1. Xác thực bằng chứng (evidence code) do mô hình trích dẫn phải thực sự tồn tại
   trong student_code hoặc compiler_error.
2. Chuẩn hóa khoảng trắng và hỗ trợ fuzzy matching có giới hạn chặt chẽ (bounded fuzzy matching).
3. Loại bỏ các dòng/mệnh đề mã do mô hình tự bịa đặt (fabricated lines).
4. Từ chối bằng chứng rò rỉ từ lời giải mẫu (reference solution) hoặc đề bài khi sinh viên chưa viết.
5. Giới hạn độ dài và số lượng mục bằng chứng ở ngưỡng hợp lý.
6. Hạ độ tin cậy (confidence) của chẩn đoán nếu không còn bằng chứng hợp lệ (confidence <= 0.4).
7. Đánh dấu chẩn đoán thành bất định (uncertain) khi một chẩn đoán tự tin bị mất hết bằng chứng.
"""

import difflib
import re
from typing import Any, Optional

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    IssueSeverity,
    TutorDiagnosis,
    TutorEvidence,
    TutorResponse,
)


class GroundingResult:
    """Kết quả kiểm định tính xác thực của một đoạn mã bằng chứng."""

    def __init__(
        self,
        is_grounded: bool,
        evidence: Optional[TutorEvidence] = None,
        rejection_reason: Optional[str] = None,
        is_reference_leakage: bool = False,
        is_fabricated: bool = False,
    ):
        self.is_grounded = is_grounded
        self.evidence = evidence
        self.rejection_reason = rejection_reason
        self.is_reference_leakage = is_reference_leakage
        self.is_fabricated = is_fabricated

    def __repr__(self) -> str:
        return (
            f"GroundingResult(grounded={self.is_grounded}, "
            f"fabricated={self.is_fabricated}, "
            f"leakage={self.is_reference_leakage}, "
            f"reason={self.rejection_reason})"
        )


class EvidenceGroundingValidator:
    """
    Bộ kiểm định tính có căn cứ (evidence-grounding) của phản hồi từ gia sư AI.
    """

    MAX_EVIDENCE_LENGTH: int = 600
    MAX_UNGROUNDED_CONFIDENCE: float = 0.40

    @classmethod
    def normalize_whitespace(cls, text: str) -> str:
        """Thu gọn toàn bộ khoảng trắng/tab/xuống dòng liên tiếp thành 1 dấu cách duy nhất."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    @classmethod
    def compact_tokens(cls, text: str) -> str:
        """
        Nén chuỗi mã nguồn bằng cách loại bỏ khoảng trắng dư thừa quanh
        các toán tử và dấu phân cách cú pháp C#.
        """
        if not text:
            return ""
        norm = cls.normalize_whitespace(text)
        # Bỏ khoảng trắng trước và sau các ký tự phân cách C#
        compact = re.sub(r"\s*([;,{}().=+\-*/<>!&|:?\[\]])\s*", r"\1", norm)
        return compact

    @classmethod
    def extract_code_lines(cls, text: str) -> list[str]:
        """Tách văn bản thành các dòng mã nguồn có nghĩa (bỏ dòng trắng và comment đơn thuần)."""
        lines = []
        for raw_line in text.splitlines():
            line = raw_line.strip()
            # Bỏ dòng trắng hoặc chỉ chứa comment
            if not line or line.startswith("//"):
                continue
            lines.append(line)
        return lines

    @classmethod
    def extract_identifiers(cls, text: str) -> set[str]:
        """Trích xuất danh sách tên định danh (biến, kiểu, hàm) từ đoạn mã."""
        keywords = {
            "public", "private", "protected", "internal", "static", "void", "int",
            "string", "double", "decimal", "float", "bool", "class", "get", "set",
            "return", "if", "else", "new", "this", "null", "true", "false", "for",
            "while", "foreach", "in", "override", "virtual", "base",
        }
        words = set(re.findall(r"\b[a-zA-Z_]\w*\b", text))
        return words - keywords

    @classmethod
    def is_line_grounded(
        cls,
        line: str,
        source_compact: str,
        source_lines_compact: list[str],
    ) -> bool:
        """
        Kiểm tra một dòng mã bằng chứng có xuất hiện trong mã nguồn với bounded fuzzy matching.
        """
        line_compact = cls.compact_tokens(line)
        if not line_compact:
            return True

        # 1. Khớp chuỗi con trực tiếp trong toàn bộ mã nén
        if line_compact in source_compact:
            return True

        # 2. Bounded fuzzy matching: So sánh từng dòng nén với ngưỡng tương đồng cao (ratio >= 0.88)
        for s_line in source_lines_compact:
            if not s_line:
                continue
            if line_compact == s_line or line_compact in s_line or s_line in line_compact:
                return True
            ratio = difflib.SequenceMatcher(None, line_compact, s_line).ratio()
            if ratio >= 0.88:
                return True

        return False

    @classmethod
    def detect_reference_solution_leakage(
        cls,
        evidence_code: str,
        student_code: str,
        compiler_error: Optional[str] = None,
        reference_solution: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> bool:
        """
        Phát hiện mô hình lấy mã từ lời giải mẫu hoặc đề bài và gán nhầm là mã của sinh viên.
        Nếu bằng chứng khớp với reference/problem nhưng KHÔNG hề có trong student_code/compiler_error.
        """
        reference_corpus = ""
        if reference_solution:
            reference_corpus += " " + reference_solution
        if problem_statement:
            reference_corpus += " " + problem_statement

        if not reference_corpus.strip():
            return False

        ev_compact = cls.compact_tokens(evidence_code)
        if not ev_compact or len(ev_compact) < 5:
            return False

        student_compiler_corpus = student_code + " " + (compiler_error or "")
        student_compact = cls.compact_tokens(student_compiler_corpus)

        ref_compact = cls.compact_tokens(reference_corpus)

        # Nếu mã bằng chứng có trong reference/problem nhưng vắng mặt trong student code
        in_reference = ev_compact in ref_compact
        in_student = ev_compact in student_compact

        if in_reference and not in_student:
            return True

        return False

    @classmethod
    def validate_evidence_snippet(
        cls,
        evidence: Optional[TutorEvidence],
        *,
        student_code: str,
        compiler_error: Optional[str] = None,
        reference_solution: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> GroundingResult:
        """
        Xác thực toàn diện một TutorEvidence đối với bài nộp của sinh viên.
        """
        if not evidence or not evidence.code or not evidence.code.strip():
            return GroundingResult(
                is_grounded=False,
                evidence=None,
                rejection_reason="Bằng chứng rỗng hoặc không cung cấp mã nguồn trích dẫn.",
            )

        raw_evidence_code = evidence.code.strip()

        # 1. Giới hạn độ dài bằng chứng tối đa
        truncated_code = raw_evidence_code
        if len(truncated_code) > cls.MAX_EVIDENCE_LENGTH:
            truncated_code = truncated_code[: cls.MAX_EVIDENCE_LENGTH].strip() + " ..."

        # 2. Kiểm tra rò rỉ từ lời giải mẫu / đề bài
        if cls.detect_reference_solution_leakage(
            evidence_code=raw_evidence_code,
            student_code=student_code,
            compiler_error=compiler_error,
            reference_solution=reference_solution,
            problem_statement=problem_statement,
        ):
            return GroundingResult(
                is_grounded=False,
                evidence=None,
                rejection_reason="Bằng chứng bị rò rỉ từ lời giải mẫu hoặc đề bài mà sinh viên chưa hề nộp.",
                is_reference_leakage=True,
            )

        # 3. Chuẩn bị ngữ cảnh nguồn từ student_code và compiler_error
        source_corpus = student_code + "\n" + (compiler_error or "")
        source_compact = cls.compact_tokens(source_corpus)
        source_lines = cls.extract_code_lines(source_corpus)
        source_lines_compact = [cls.compact_tokens(l) for l in source_lines]

        # Kiểm tra exact hoặc compact substring toàn phần trước
        ev_compact = cls.compact_tokens(raw_evidence_code)
        if ev_compact in source_compact:
            validated_evidence = TutorEvidence(
                code=truncated_code,
                reason=evidence.reason.strip(),
            )
            return GroundingResult(is_grounded=True, evidence=validated_evidence)

        # 4. Kiểm tra từng dòng/mệnh đề trong bằng chứng (loại bỏ fabricated lines)
        ev_lines = cls.extract_code_lines(raw_evidence_code)
        if not ev_lines:
            return GroundingResult(
                is_grounded=False,
                evidence=None,
                rejection_reason="Bằng chứng không chứa dòng mã nguồn thực thi hợp lệ.",
            )

        # Kiểm tra định danh: Các định danh quan trọng trong evidence phải có trong source
        source_identifiers = cls.extract_identifiers(source_corpus)
        for ev_line in ev_lines:
            line_identifiers = cls.extract_identifiers(ev_line)
            # Nếu có định danh mới hoàn toàn không xuất hiện trong bài nộp -> Fabricated!
            unknown_ids = line_identifiers - source_identifiers
            if unknown_ids and len(line_identifiers) > 0 and len(source_identifiers) > 0:
                # Nếu tất cả định danh của dòng đều lạ hoặc dòng chứa định danh chưa từng xuất hiện
                # cho phép một số từ khóa phổ biến nhưng cấm biến bịa
                return GroundingResult(
                    is_grounded=False,
                    evidence=None,
                    rejection_reason=f"Bằng chứng chứa dòng mã bịa đặt với các định danh không tồn tại trong bài nộp: {', '.join(unknown_ids)}",
                    is_fabricated=True,
                )

            # Kiểm tra dòng có grounded theo bounded fuzzy matching không
            if not cls.is_line_grounded(ev_line, source_compact, source_lines_compact):
                return GroundingResult(
                    is_grounded=False,
                    evidence=None,
                    rejection_reason=f"Dòng mã '{ev_line}' không thể tìm thấy trong mã nguồn sinh viên hoặc lỗi biên dịch.",
                    is_fabricated=True,
                )

        # Tất cả dòng đều hợp lệ và grounded
        validated_evidence = TutorEvidence(
            code=truncated_code,
            reason=evidence.reason.strip(),
        )
        return GroundingResult(is_grounded=True, evidence=validated_evidence)

    @classmethod
    def ground_diagnosis(
        cls,
        diagnosis: TutorDiagnosis,
        *,
        student_code: str,
        compiler_error: Optional[str] = None,
        reference_solution: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> TutorDiagnosis:
        """
        Kiểm định và chuẩn hóa tính có căn cứ cho TutorDiagnosis.
        Quy tắc sư phạm:
        - Nếu mã nguồn hợp lệ (NO_BUG) hoặc thiếu ngữ cảnh (INSUFFICIENT_CONTEXT): Không bắt buộc bằng chứng lỗi.
        - Nếu chẩn đoán là một lỗi kỹ thuật (category khác NO_BUG):
          * Bằng chứng phải có căn cứ thực tế trong student_code hoặc compiler_error.
          * Nếu bằng chứng bị từ chối / bịa đặt: Xóa bằng chứng, hạ confidence xuống <= 0.4, và đánh dấu bất định (uncertain / UNKNOWN).
          * Độ tin cậy cao không bao giờ được tồn tại khi chẩn đoán hoàn toàn không có căn cứ.
        """
        diag_dict = diagnosis.model_dump()
        category = diagnosis.category

        # NO_BUG hoặc INSUFFICIENT_CONTEXT không yêu cầu bằng chứng lỗi
        if category in (DiagnosisCategory.NO_BUG, DiagnosisCategory.INSUFFICIENT_CONTEXT):
            return diagnosis

        # Kiểm định bằng chứng
        grounding_res = cls.validate_evidence_snippet(
            diagnosis.evidence,
            student_code=student_code,
            compiler_error=compiler_error,
            reference_solution=reference_solution,
            problem_statement=problem_statement,
        )

        if grounding_res.is_grounded and grounding_res.evidence:
            diag_dict["evidence"] = grounding_res.evidence.model_dump()
            return TutorDiagnosis.model_validate(diag_dict)

        # BẰNG CHỨNG BỊ TỪ CHỐI HOẶC BỊA ĐẶT
        # 1. Xóa bằng chứng không hợp lệ
        diag_dict["evidence"] = None

        # 2. Quy tắc cốt lõi: High confidence cannot survive completely unsupported diagnosis.
        # Hạ độ tin cậy xuống mức bất định (tối đa 0.40)
        original_confidence = float(diag_dict.get("confidence", 0.5))
        penalized_confidence = min(cls.MAX_UNGROUNDED_CONFIDENCE, round(original_confidence * 0.4, 2))
        diag_dict["confidence"] = max(0.1, penalized_confidence)

        # 3. Đánh dấu bất định: Chuyển category sang UNKNOWN và hạ severity
        diag_dict["category"] = DiagnosisCategory.UNKNOWN.value
        diag_dict["issue_type"] = "unclassified_issue"
        diag_dict["severity"] = IssueSeverity.WARNING.value
        diag_dict["possible_misconception"] = None

        loc = diag_dict.get("location")
        diag_dict["location"] = f"unverified: {loc}" if loc else "unverified location"

        return TutorDiagnosis.model_validate(diag_dict)

    @classmethod
    def validate_and_ground_response(
        cls,
        response: TutorResponse,
        *,
        student_code: str,
        compiler_error: Optional[str] = None,
        reference_solution: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> TutorResponse:
        """
        Kiểm định tính xác thực của toàn bộ TutorResponse, đồng bộ lại diagnosis và top-level fields.
        """
        grounded_diagnosis = cls.ground_diagnosis(
            response.diagnosis,
            student_code=student_code,
            compiler_error=compiler_error,
            reference_solution=reference_solution,
            problem_statement=problem_statement,
        )

        resp_dict = response.model_dump()
        resp_dict["diagnosis"] = grounded_diagnosis.model_dump()
        resp_dict["evidence"] = (
            grounded_diagnosis.evidence.model_dump()
            if grounded_diagnosis.evidence
            else None
        )

        # Nếu chẩn đoán bị đánh dấu bất định do thiếu bằng chứng, điều chỉnh gợi ý sư phạm
        if grounded_diagnosis.category == DiagnosisCategory.UNKNOWN and response.diagnosis.category != DiagnosisCategory.UNKNOWN:
            resp_dict["teaching_strategy"] = "uncertainty_clarification"
            resp_dict["next_action"] = "Xem lại đoạn mã hiện tại hoặc kiểm tra lại thông báo từ trình biên dịch để cung cấp thêm ngữ cảnh."

        return TutorResponse.model_validate(resp_dict)
