"""
Verification Subsystem - Hệ thống xác minh lần thử lại của sinh viên (APT-014).

Nguyên tắc bảo mật:
- TUYỆT ĐỐI KHÔNG thực thi mã C# tùy ý trực tiếp trên production backend.
- Phân tích tĩnh, so khớp mẫu chuẩn và chẩn đoán cấu trúc qua DiagnosisSubsystem.
- Kiến trúc mở với ExecutionBackend trừu tượng, sẵn sàng mở rộng Sandboxed Compiler Runner trong tương lai.
- Tính xác thực sư phạm: Không mạo nhận phân tích tĩnh tương đương với việc biên dịch/thực thi thực tế.
- Nhãn chuẩn hóa: likely_resolved, still_present, new_issue, needs_execution_to_confirm.
"""

from abc import ABC, abstractmethod
import logging
import re
from typing import Any, Optional

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    TutorDiagnosis,
    TutorVerifyRequest,
    TutorVerifyResponse,
    VerificationStatus,
)
from app.tutor.diagnosis import DiagnosisSubsystem

logger = logging.getLogger(__name__)

SECURITY_BOUNDARY_NOTE = (
    "Đánh giá dựa trên phân tích tĩnh và quy chuẩn sư phạm C# OOP; "
    "chưa qua môi trường thực thi hộp cát cô lập (sandboxed execution)."
)


class ExecutionBackend(ABC):
    """Giao diện trừu tượng cho backend phân tích hoặc thực thi mã nguồn."""

    @abstractmethod
    async def inspect_or_execute(
        self,
        code: str,
        problem_statement: Optional[str] = None,
        previous_code: Optional[str] = None,
    ) -> TutorDiagnosis:
        """Thực hiện phân tích tĩnh hoặc thực thi hộp cát mã nguồn."""
        pass


class StaticAndPatternExecutionBackend(ExecutionBackend):
    """
    Backend V1: Hoàn toàn phân tích tĩnh và so khớp mẫu chuẩn.
    TUYỆT ĐỐI KHÔNG sinh subprocess hoặc gọi dotnet run/exec trên production.
    """

    async def inspect_or_execute(
        self,
        code: str,
        problem_statement: Optional[str] = None,
        previous_code: Optional[str] = None,
    ) -> TutorDiagnosis:
        return DiagnosisSubsystem.diagnose(
            student_code=code,
            compiler_error=None,
            problem_statement=problem_statement,
        )


class SandboxedCompilerBackend(ExecutionBackend):
    """
    Placeholder cho Sandboxed Execution Backend (Docker/WASM/gVisor) trong tương lai.
    """

    async def inspect_or_execute(
        self,
        code: str,
        problem_statement: Optional[str] = None,
        previous_code: Optional[str] = None,
    ) -> TutorDiagnosis:
        raise NotImplementedError(
            "Môi trường thực thi hộp cát cô lập (Sandboxed Compiler) chưa được cấu hình trong phiên bản V1."
        )


class VerificationService:
    """
    Dịch vụ điều phối xác minh lần thử lại của sinh viên (Student Retry Verification).
    """

    def __init__(self, backend: Optional[ExecutionBackend] = None):
        self._backend: ExecutionBackend = backend or StaticAndPatternExecutionBackend()

    async def verify_retry(self, request: TutorVerifyRequest) -> TutorVerifyResponse:
        """
        Xác minh bài sửa của sinh viên dựa trên đối chiếu chẩn đoán cũ và mới.
        """
        # 1. Xác định chẩn đoán bài cũ
        original_diag = request.original_diagnosis
        if not original_diag and request.previous_code:
            original_diag = DiagnosisSubsystem.diagnose(
                student_code=request.previous_code,
                compiler_error=None,
                problem_statement=request.problem_statement,
            )

        orig_issue = original_diag.issue_type if original_diag else None

        # 2. Phân tích mã mới qua execution backend (V1: tĩnh)
        new_diag = await self._backend.inspect_or_execute(
            code=request.revised_student_code,
            problem_statement=request.problem_statement,
            previous_code=request.previous_code,
        )

        new_category = new_diag.category
        new_issue = new_diag.issue_type

        # 3. Phân loại trạng thái và tổng hợp kết quả
        remaining_issues: list[str] = []
        new_issues: list[str] = []

        # Kiểm tra tính phức tạp cần thực thi thực tế (loop / recursive algorithm)
        has_complex_runtime_logic = self._has_complex_runtime_patterns(request.revised_student_code)

        if new_category == DiagnosisCategory.NO_BUG:
            if has_complex_runtime_logic:
                status = VerificationStatus.NEEDS_EXECUTION_TO_CONFIRM
                resolved = True
                confidence = 0.75
                feedback = (
                    "Đoạn mã sửa đổi đã tuân thủ tốt các nguyên lý hướng đối tượng C# theo phân tích cấu trúc tĩnh. "
                    "Tuy nhiên, do giải thuật có cấu trúc lặp/điều kiện phức tạp, chương trình cần được biên dịch "
                    "và chạy thử nghiệm thực tế với bộ test cases để khẳng định kết quả tuyệt đối."
                )
                next_action = "Chạy thử nghiệm chương trình trong IDE cục bộ để kiểm tra các trường hợp biên."
            else:
                status = VerificationStatus.LIKELY_RESOLVED
                resolved = True
                confidence = 0.90
                feedback = (
                    "Rất tốt! Phân tích cấu trúc cho thấy đoạn mã sửa đổi đã giải quyết được vấn đề trước đó "
                    "và tuân thủ đúng các nguyên tắc lập trình hướng đối tượng C#."
                )
                next_action = "Bạn có thể tiến hành nộp bài hoặc tiếp tục thử thách với các bài toán tiếp theo."

        elif orig_issue and (new_issue == orig_issue or "still" in new_issue):
            status = VerificationStatus.STILL_PRESENT
            resolved = False
            confidence = 0.88
            remaining_issues.append(f"Vấn đề '{new_issue}' tại {new_diag.location or 'mã nguồn'} vẫn chưa được khắc phục.")
            feedback = (
                f"Đoạn mã sửa đổi vẫn còn xuất hiện vấn đề '{new_issue}'. "
                "Hãy rà soát lại gợi ý sư phạm để hiểu rõ cách khắc phục."
            )
            next_action = "Xem lại gợi ý có định hướng ở bước trước và chỉnh sửa lại dòng mã liên quan."

        else:
            # Phát hiện vấn đề mới phát sinh
            status = VerificationStatus.NEW_ISSUE
            resolved = False
            confidence = 0.85
            new_issues.append(f"Vấn đề mới '{new_issue}': {new_category.value}")
            feedback = (
                f"Bạn đã chỉnh sửa đoạn mã, nhưng hệ thống ghi nhận một vấn đề mới phát sinh: '{new_issue}'. "
                "Hãy cùng kiểm tra lại cú pháp hoặc cấu trúc lớp vừa thêm."
            )
            next_action = "Tập trung điều chỉnh vấn đề mới phát sinh trước khi hoàn thiện toàn bộ bài toán."

        return TutorVerifyResponse(
            verification_status=status,
            resolved=resolved,
            remaining_issues=remaining_issues,
            new_issues=new_issues,
            feedback=feedback,
            next_action=next_action,
            confidence=confidence,
            security_boundary_note=SECURITY_BOUNDARY_NOTE,
            session_id=request.session_id,
        )

    @staticmethod
    def _has_complex_runtime_patterns(code: str) -> bool:
        """Kiểm tra xem mã có logic runtime phức tạp cần test cases thực tế để khẳng định hay không."""
        complex_regexes = [
            r"\bwhile\s*\(",
            r"\bfor\s*\(",
            r"\bforeach\s*\(",
            r"\bdo\s*\{",
            r"\bThread\.",
            r"\bTask\.",
            r"\basync\b",
        ]
        return any(re.search(pat, code) for pat in complex_regexes)
