"""
Deterministic Student Skill Mastery Model (APT-018) - Version 1.

Cung cấp mô hình tính toán và cập nhật độ thuần thục kỹ năng (Mastery Score)
tất định, minh bạch và có thể kiểm tra (inspectable) dành cho gia sư C# OOP.

NGUYÊN TẮC CỐT LÕI (V1):
1. Không triển khai Bayesian Knowledge Tracing (BKT) phức tạp trong giai đoạn này.
2. Trạng thái khởi tạo là trung tính / chưa xác định: INITIAL_MASTERY = 0.5
   (tránh giả định độ chắc chắn khi chưa có dữ liệu quan sát).
3. Công thức cập nhật dựa trên bước nhảy có trọng số sư phạm (Pedagogical Step Rule):
   M_{t+1} = clamp(M_t + \\Delta(event), 0.0, 1.0)
4. Điểm số luôn được kẹp chặt trong khoảng [0.0, 1.0] và làm tròn 4 chữ số thập phân.
5. Cùng chuỗi sự kiện luôn tạo ra cùng kết quả điểm số (Deterministic Guarantee).
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class MasteryEvent(str, Enum):
    """
    Các loại sự kiện nộp bài và kết quả luyện tập của sinh viên.
    """
    INDEPENDENT_SUCCESS = "independent_success"
    HINT_L1_SUCCESS = "hint_l1_success"
    HINT_L2_L3_SUCCESS = "hint_l2_l3_success"
    EXPLICIT_SOLUTION_L4 = "explicit_solution_l4"
    UNRESOLVED_ATTEMPT = "unresolved_attempt"


@dataclass(frozen=True)
class EventWeightInfo:
    """Mô tả trọng số và lý giải sư phạm cho từng sự kiện."""
    delta: float
    description: str
    pedagogical_rationale: str


EVENT_WEIGHTS: dict[MasteryEvent, EventWeightInfo] = {
    MasteryEvent.INDEPENDENT_SUCCESS: EventWeightInfo(
        delta=0.15,
        description="Giải thành công độc lập không cần gợi ý",
        pedagogical_rationale=(
            "Bằng chứng mạnh mẽ nhất về sự tự chủ và thuần thục kỹ năng; "
            "tăng điểm tối đa (+0.15)."
        ),
    ),
    MasteryEvent.HINT_L1_SUCCESS: EventWeightInfo(
        delta=0.10,
        description="Giải thành công sau khi nhận gợi ý Socratic Level 1",
        pedagogical_rationale=(
            "Sinh viên chỉ cần một câu hỏi gợi mở định hướng tư duy để tự sửa lỗi; "
            "thể hiện hiểu biết tốt nhưng chưa hoàn toàn độc lập (+0.10)."
        ),
    ),
    MasteryEvent.HINT_L2_L3_SUCCESS: EventWeightInfo(
        delta=0.05,
        description="Giải thành công sau gợi ý giải thích khái niệm (L2) hoặc chỉ vị trí (L3)",
        pedagogical_rationale=(
            "Sinh viên cần được nhắc lại khái niệm hoặc chỉ rõ vị trí và hướng sửa; "
            "vẫn là một bước tiến học tập nhưng đóng góp thuần thục ít hơn (+0.05)."
        ),
    ),
    MasteryEvent.EXPLICIT_SOLUTION_L4: EventWeightInfo(
        delta=-0.05,
        description="Xem lời giải chi tiết Level 4 (solution revealed)",
        pedagogical_rationale=(
            "Sinh viên đã được cấp lời giải hoàn chỉnh nên bài nộp này không phản ánh "
            "năng lực tự thân của sinh viên; giảm nhẹ điểm (-0.05) để khuyến khích tự thử lại."
        ),
    ),
    MasteryEvent.UNRESOLVED_ATTEMPT: EventWeightInfo(
        delta=-0.15,
        description="Lần thử thất bại hoặc bỏ cuộc khi bài tập chưa được sửa đúng",
        pedagogical_rationale=(
            "Bằng chứng cho thấy sinh viên còn vướng mắc hoặc ngộ nhận với kỹ năng này; "
            "giảm điểm tương đương một lần làm đúng độc lập (-0.15)."
        ),
    ),
}


class DeterministicMasteryModel:
    """
    Mô hình ước lượng độ thuần thục kỹ năng tất định cho sinh viên C# OOP V1.
    """

    INITIAL_MASTERY: float = 0.5
    MIN_SCORE: float = 0.0
    MAX_SCORE: float = 1.0

    @classmethod
    def calculate_next_mastery(
        cls,
        current_score: float,
        event: MasteryEvent,
    ) -> float:
        """
        Tính điểm thuần thục tiếp theo:
        M_{t+1} = clamp(M_t + \\Delta(event), 0.0, 1.0)
        """
        if event not in EVENT_WEIGHTS:
            raise ValueError(f"Sự kiện không hợp lệ: {event}")

        weight_info = EVENT_WEIGHTS[event]
        new_score = current_score + weight_info.delta
        clamped_score = max(cls.MIN_SCORE, min(cls.MAX_SCORE, new_score))
        return round(clamped_score, 4)

    @classmethod
    def classify_attempt_event(
        cls,
        *,
        resolved: bool,
        highest_hint_level_used: int = 0,
        solution_revealed: bool = False,
    ) -> MasteryEvent:
        """
        Tự động phân loại sự kiện luyện tập dựa trên kết quả xác thực và tiến trình gợi ý:
        - solution_revealed = True hoặc hint_level >= 4 -> EXPLICIT_SOLUTION_L4
        - resolved = False -> UNRESOLVED_ATTEMPT
        - resolved = True:
          + hint_level == 0 -> INDEPENDENT_SUCCESS
          + hint_level == 1 -> HINT_L1_SUCCESS
          + hint_level in (2, 3) -> HINT_L2_L3_SUCCESS
          + hint_level >= 4 -> EXPLICIT_SOLUTION_L4
        """
        if solution_revealed or highest_hint_level_used >= 4:
            return MasteryEvent.EXPLICIT_SOLUTION_L4

        if not resolved:
            return MasteryEvent.UNRESOLVED_ATTEMPT

        if highest_hint_level_used <= 0:
            return MasteryEvent.INDEPENDENT_SUCCESS
        elif highest_hint_level_used == 1:
            return MasteryEvent.HINT_L1_SUCCESS
        elif highest_hint_level_used in (2, 3):
            return MasteryEvent.HINT_L2_L3_SUCCESS
        else:
            return MasteryEvent.EXPLICIT_SOLUTION_L4

    @classmethod
    def apply_event_to_state(
        cls,
        *,
        current_score: float,
        success_count: int,
        failure_count: int,
        hint_count: int,
        event: MasteryEvent,
        hints_used_in_attempt: int = 0,
        practice_time: Optional[datetime] = None,
    ) -> dict[str, Any]:
        """
        Cập nhật toàn bộ trạng thái độ thuần thục từ một sự kiện:
        - Tính điểm mastery mới.
        - Cập nhật success_count / failure_count / hint_count.
        - Gán last_practiced_at.
        """
        next_score = cls.calculate_next_mastery(current_score, event)

        new_success = success_count
        new_failure = failure_count
        new_hints = hint_count + max(0, hints_used_in_attempt)

        if event in (
            MasteryEvent.INDEPENDENT_SUCCESS,
            MasteryEvent.HINT_L1_SUCCESS,
            MasteryEvent.HINT_L2_L3_SUCCESS,
        ):
            new_success += 1
        elif event in (
            MasteryEvent.EXPLICIT_SOLUTION_L4,
            MasteryEvent.UNRESOLVED_ATTEMPT,
        ):
            new_failure += 1

        timestamp = practice_time or datetime.now(timezone.utc)

        return {
            "mastery_score": next_score,
            "success_count": new_success,
            "failure_count": new_failure,
            "hint_count": new_hints,
            "last_practiced_at": timestamp,
        }

    @classmethod
    def get_formula_documentation(cls) -> dict[str, Any]:
        """
        Trả về tài liệu mô tả chi tiết, minh bạch và có thể kiểm tra (inspectable) của công thức V1.
        """
        return {
            "formula_name": "Deterministic Piecewise Additive Mastery Rule",
            "version": "v1",
            "initial_mastery": cls.INITIAL_MASTERY,
            "score_bounds": [cls.MIN_SCORE, cls.MAX_SCORE],
            "mathematical_formula": "M_{t+1} = clamp(M_t + \\Delta(event), 0.0, 1.0)",
            "description": (
                "Quy tắc cập nhật điểm thuần thục kỹ năng tất định cho V1. "
                "Điểm số khởi tạo ở mức trung tính 0.5 (chưa có bằng chứng để khẳng định chắc chắn). "
                "Mỗi bài tập tác động một lượng delta cụ thể tùy thuộc vào mức độ tự chủ của sinh viên "
                "và việc có sử dụng các cấp độ gợi ý hay không."
            ),
            "event_deltas": {
                ev.value: {
                    "delta": info.delta,
                    "description": info.description,
                    "pedagogical_rationale": info.pedagogical_rationale,
                }
                for ev, info in EVENT_WEIGHTS.items()
            },
            "initial_state_explanation": (
                "Điểm khởi tạo bằng 0.5 đại diện cho trạng thái trung tính/không chắc chắn "
                "(neutral/unknown prior), tránh việc giả định vô cớ sinh viên chưa biết gì (0.0) "
                "hoặc đã thành thạo (1.0) trước khi có bất kỳ tương tác giải bài nào."
            ),
            "clamping_rule": (
                "Điểm số luôn được kẹp trong đoạn [0.0, 1.0]. "
                "Nếu M_t + delta > 1.0, kết quả là 1.0. "
                "Nếu M_t + delta < 0.0, kết quả là 0.0."
            ),
        }
