"""
SolutionLeakageGuard - Bộ kiểm định và ngăn chặn rò rỉ giải pháp sớm (APT-012).

Mục đích:
Phát hiện và ngăn chặn khi các cấp độ gợi ý 1, 2, và 3 tiết lộ quá nhiều lời giải
(premature solution leakage) trong quá trình gia sư lập trình C# OOP.

Kiểm tra 5 dạng rò rỉ tất định:
1. Toàn bộ reference solution xuất hiện nguyên văn (verbatim).
2. Dòng mã sửa chữa (corrected line) xuất hiện nguyên văn ở các cấp độ sớm (Level 1, 2).
3. Khối mã markdown lớn (large code blocks) chứa mã sửa chữa bài toán ở Level 1-3.
4. Mẫu câu mớm đáp án trực tiếp ("thay X bằng Y", "sửa thành Y", "replace X with Y") ở Level 1, 2.
5. Metadata mô hình đặt solution_revealed = False nhưng phản hồi chứa mã giải hoàn chỉnh.

Nguyên tắc:
- Ưu tiên kiểm tra tất định trước (deterministic checks first).
- Hỗ trợ ngoại lệ theo nhiệm vụ (task-specific exceptions) cho các từ khóa độc lập như "this", "base".
- Khi phát hiện rò rỉ: tự động hạ cấp về deterministic safe hint từ HintManager và ghi vết validator_actions.
- Bảo toàn Level 4: Cho phép Level 4 hiển thị mã giải hoàn chỉnh (solution_revealed = True).
"""

import logging
import re
from typing import Any, Optional, Set
from pydantic import BaseModel, Field

from app.schemas.tutor_schema import TutorResponse
from app.tutor.hint_manager import HintManager

logger = logging.getLogger(__name__)


class LeakageCheckResult(BaseModel):
    """Kết quả kiểm định rò rỉ giải pháp."""

    has_leakage: bool = False
    leakage_type: Optional[str] = None
    details: str = "Không phát hiện rò rỉ giải pháp."
    matched_snippet: Optional[str] = None


class SolutionLeakageGuard:
    """
    Bộ bảo vệ chống rò rỉ giải pháp lập trình sớm (SolutionLeakageGuard).
    """

    # Danh sách các từ khóa kỹ thuật độc lập được phép xuất hiện trong giải thích lý thuyết
    ALLOWED_CONCEPT_KEYWORDS: Set[str] = {
        "this",
        "base",
        "override",
        "virtual",
        "class",
        "public",
        "private",
        "protected",
        "get",
        "set",
        "interface",
        "void",
        "return",
        "new",
        "int",
        "string",
        "bool",
        "double",
        "float",
        "decimal",
        "value",
    }

    # Regex nhận diện các mẫu câu mớm đáp án trực tiếp ở Level 1 và Level 2
    DIRECT_REPLACEMENT_PATTERNS: list[re.Pattern] = [
        re.compile(r"(?i)\b(?:thay\s+(?:đoạn\s+|câu\s+lệnh\s+)?['\"`]?(?P<src>[^'\"`\n]+)['\"`]?\s+bằng\s+['\"`]?(?P<dst>[^'\"`\n]+)['\"`]?)", re.UNICODE),
        re.compile(r"(?i)\b(?:thay\s+thế\s+.*bằng\s+.*)", re.UNICODE),
        re.compile(r"(?i)\b(?:sửa\s+(?:thành|thành\s+câu\s+lệnh)\s+['\"`]?(?P<target>[^'\"`\n]+)['\"`]?)", re.UNICODE),
        re.compile(r"(?i)\b(?:đổi\s+.*thành\s+.*)", re.UNICODE),
        re.compile(r"(?i)\b(?:viết\s+(?:lại\s+)?thành\s+['\"`]?(?P<target>[^'\"`\n]+)['\"`]?)", re.UNICODE),
        re.compile(r"(?i)\b(?:chỉ\s+cần\s+(?:sửa|thay)\s+.*bằng\s+.*)", re.UNICODE),
        re.compile(r"(?i)\b(?:replace\s+['\"`]?(?P<src>[^'\"`\n]+)['\"`]?\s+with\s+['\"`]?(?P<dst>[^'\"`\n]+)['\"`]?)", re.UNICODE),
        re.compile(r"(?i)\b(?:change\s+['\"`]?(?P<src>[^'\"`\n]+)['\"`]?\s+to\s+['\"`]?(?P<dst>[^'\"`\n]+)['\"`]?)", re.UNICODE),
    ]

    # Các mẫu câu sửa canonical C# OOP dễ bị mớm ở level sớm
    CANONICAL_REPAIR_REGEXES: list[tuple[re.Pattern, str]] = [
        (
            re.compile(r"(?i)\bthis\.[a-zA-Z0-9_]+\s*=\s*[a-zA-Z0-9_]+;"),
            "Phép gán hoàn chỉnh 'this.field = param;' bị lộ nguyên văn",
        ),
        (
            re.compile(r"(?i)\breturn\s+_[a-zA-Z0-9_]+;"),
            "Câu lệnh trả về backing field 'return _field;' bị lộ nguyên văn",
        ),
        (
            re.compile(r"(?i)\b_[a-zA-Z0-9_]+\s*=\s*value;"),
            "Câu lệnh gán setter backing field '_field = value;' bị lộ nguyên văn",
        ),
    ]

    @classmethod
    def check_leakage(
        cls,
        tutor_response_text: str,
        hint_level: int,
        student_code: Optional[str] = None,
        reference_solution: Optional[str] = None,
        solution_revealed: bool = False,
        allowed_keywords: Optional[Set[str]] = None,
    ) -> LeakageCheckResult:
        """
        Kiểm tra rò rỉ giải pháp tất định cho văn bản phản hồi.
        Level 4 luôn được phép hiển thị giải pháp.
        """
        target_level = max(1, min(4, int(hint_level)))

        # Level 4 được phép tiết lộ hoàn toàn mã giải
        if target_level >= 4:
            return LeakageCheckResult(
                has_leakage=False,
                details="Level 4 cho phép hiển thị giải pháp tường minh.",
            )

        text = tutor_response_text.strip()
        if not text:
            return LeakageCheckResult(has_leakage=False)

        effective_allowed = set(cls.ALLOWED_CONCEPT_KEYWORDS)
        if allowed_keywords:
            effective_allowed.update(allowed_keywords)

        # 1. Kiểm tra mâu thuẫn metadata: claim solution_revealed=True ở level < 4
        if solution_revealed:
            return LeakageCheckResult(
                has_leakage=True,
                leakage_type="false_unrevealed_metadata",
                details=f"Metadata solution_revealed=True không được phép khi hint_level={target_level} < 4.",
                matched_snippet="solution_revealed=True",
            )

        # 2. Kiểm tra full reference solution appearing verbatim
        if reference_solution and reference_solution.strip():
            ref_clean = cls._normalize_code_whitespace(reference_solution)
            text_clean = cls._normalize_code_whitespace(text)
            if len(ref_clean) >= 20 and ref_clean in text_clean:
                return LeakageCheckResult(
                    has_leakage=True,
                    leakage_type="full_reference_verbatim",
                    details="Toàn bộ lời giải mẫu (reference solution) xuất hiện nguyên văn trong phản hồi.",
                    matched_snippet=reference_solution[:120],
                )

        # 3. Kiểm tra corrected source line appearing verbatim ở Level 1 và 2
        if reference_solution and student_code and target_level <= 2:
            corrected_lines = cls._extract_corrected_lines(
                reference_solution=reference_solution,
                student_code=student_code,
                allowed_keywords=effective_allowed,
            )
            for cline in corrected_lines:
                cline_norm = cls._normalize_code_whitespace(cline)
                if len(cline_norm) >= 8 and cline_norm in cls._normalize_code_whitespace(text):
                    return LeakageCheckResult(
                        has_leakage=True,
                        leakage_type="corrected_line_verbatim",
                        details=f"Dòng mã đã sửa '{cline}' xuất hiện nguyên văn ở hint level {target_level}.",
                        matched_snippet=cline,
                    )

        # 4. Kiểm tra các mẫu câu canonical repair xuất hiện ở Level 1 và 2
        if target_level <= 2:
            for pattern, reason in cls.CANONICAL_REPAIR_REGEXES:
                match = pattern.search(text)
                if match:
                    # Kiểm tra xem có phải chỉ là nhắc đến từ khóa riêng lẻ không
                    matched_str = match.group(0)
                    if matched_str.strip(" ;") not in effective_allowed:
                        return LeakageCheckResult(
                            has_leakage=True,
                            leakage_type="corrected_line_verbatim",
                            details=f"{reason} ở hint level {target_level}.",
                            matched_snippet=matched_str,
                        )

        # 5. Kiểm tra large code blocks containing repair
        code_blocks = cls._extract_code_blocks(text)
        if code_blocks:
            for block in code_blocks:
                non_empty_lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
                # Ở Level 1 và Level 2: cấm code blocks chứa mã giải sửa chữa
                if target_level <= 2 and len(non_empty_lines) >= 1:
                    # Nếu code block chứa các cấu trúc gán, return, hoặc sửa member
                    has_repair_code = any(
                        ("=" in ln or "return" in ln or "{" in ln or ";" in ln)
                        for ln in non_empty_lines
                    )
                    if has_repair_code:
                        return LeakageCheckResult(
                            has_leakage=True,
                            leakage_type="large_repair_code_block",
                            details=f"Khối mã ({len(non_empty_lines)} dòng) chứa mã sửa bài xuất hiện ở hint level {target_level}.",
                            matched_snippet=block[:120],
                        )
                # Ở Level 3: cấm code block sửa chữa hoàn chỉnh (>= 3 dòng)
                elif target_level == 3 and len(non_empty_lines) >= 3:
                    return LeakageCheckResult(
                        has_leakage=True,
                        leakage_type="large_repair_code_block",
                        details=f"Khối mã sửa chữa hoàn chỉnh ({len(non_empty_lines)} dòng) xuất hiện ở hint level 3.",
                        matched_snippet=block[:120],
                    )

        # 6. Kiểm tra direct "replace X with Y" answer ở Level 1 và 2
        if target_level <= 2:
            for pattern in cls.DIRECT_REPLACEMENT_PATTERNS:
                match = pattern.search(text)
                if match:
                    snippet = match.group(0)
                    # Ngoại lệ: Nếu chỉ nhắc từ khóa cho phép (ví dụ: 'thay bằng từ khóa this')
                    # Kiểm tra xem có đưa đoạn code cụ thể hay câu lệnh sửa không
                    is_exception = False
                    groups = match.groupdict()
                    target_candidate = groups.get("dst") or groups.get("target") or ""
                    clean_target = target_candidate.strip(" '\\\";.`")
                    if clean_target in effective_allowed and len(clean_target.split()) <= 2:
                        is_exception = True

                    if not is_exception:
                        return LeakageCheckResult(
                            has_leakage=True,
                            leakage_type="direct_replacement_pattern",
                            details=f"Chỉ dẫn mớm đáp án trực tiếp ('{snippet[:60]}...') ở hint level {target_level}.",
                            matched_snippet=snippet,
                        )

        return LeakageCheckResult(has_leakage=False)

    @classmethod
    def sanitize_if_leaked(
        cls,
        response: TutorResponse,
        student_code: Optional[str] = None,
        reference_solution: Optional[str] = None,
        allowed_keywords: Optional[Set[str]] = None,
    ) -> TutorResponse:
        """
        Kiểm định và tự động xử lý rò rỉ:
        Nếu phát hiện rò rỉ ở level < 4:
        - Hạ cấp câu trả lời về deterministic safe hint từ HintManager.
        - Đảm bảo solution_revealed = False.
        - Ghi nhận hành động kiểm định vào validator_actions.
        """
        check_res = cls.check_leakage(
            tutor_response_text=response.tutor_response,
            hint_level=response.hint_level,
            student_code=student_code,
            reference_solution=reference_solution,
            solution_revealed=response.solution_revealed,
            allowed_keywords=allowed_keywords,
        )

        if check_res.has_leakage:
            logger.warning(
                "Phát hiện rò rỉ giải pháp sớm [%s]: %s (snippet: %s)",
                check_res.leakage_type,
                check_res.details,
                check_res.matched_snippet,
            )

            # Hạ cấp về deterministic safe hint
            safe_payload = HintManager.generate_progressive_hint(
                diagnosis=response.diagnosis,
                hint_level=response.hint_level,
                student_code=student_code,
            )

            # Cập nhật response an toàn
            response.tutor_response = safe_payload.tutor_response
            response.teaching_strategy = safe_payload.teaching_strategy
            response.next_action = safe_payload.next_action
            response.solution_revealed = False

            # Ghi nhận hành động can thiệp kiểm định
            action_record = (
                f"downgraded_to_safe_hint: {check_res.leakage_type or 'unknown'} - {check_res.details}"
            )
            if not hasattr(response, "validator_actions") or response.validator_actions is None:
                response.validator_actions = []
            response.validator_actions.append(action_record)

        return response

    # -------------------------------------------------------------
    # Các hàm phụ trợ (Helper methods)
    # -------------------------------------------------------------
    @staticmethod
    def _normalize_code_whitespace(text: str) -> str:
        """Loại bỏ khoảng trắng thừa và chuẩn hóa xuống dòng để so khớp."""
        # Loại bỏ comment một dòng //...
        no_line_comments = re.sub(r"//.*", "", text)
        # Chuẩn hóa khoảng trắng liên tiếp thành 1 dấu cách đơn
        tokens = no_line_comments.split()
        return " ".join(tokens)

    @staticmethod
    def _extract_code_blocks(text: str) -> list[str]:
        """Trích xuất tất cả các khối mã markdown ```...```."""
        pattern = re.compile(r"```(?:[a-zA-Z0-9_+-]+)?\s*([\s\S]*?)```")
        return [match.group(1).strip() for match in pattern.finditer(text)]

    @classmethod
    def _extract_corrected_lines(
        cls,
        reference_solution: str,
        student_code: str,
        allowed_keywords: Set[str],
    ) -> list[str]:
        """
        Trích xuất các dòng mã có ý nghĩa trong reference_solution mà không có trong student_code.
        """
        student_normalized_lines = {
            cls._normalize_code_whitespace(line)
            for line in student_code.splitlines()
            if line.strip()
        }

        corrected = []
        for raw_line in reference_solution.splitlines():
            line = raw_line.strip()
            if not line or line in ("{", "}", "};", "public", "private"):
                continue

            norm = cls._normalize_code_whitespace(line)
            # Nếu dòng này chỉ là 1 từ khóa đơn lẻ
            if norm in allowed_keywords:
                continue

            if norm and norm not in student_normalized_lines:
                corrected.append(line)

        return corrected
