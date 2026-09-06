"""
HintManager - Hệ thống quản lý và điều phối gợi ý sư phạm tiến dần (Progressive Hint System).

Cung cấp 4 cấp độ gợi ý tiến dần:
- Level 1: Socratic question (Câu hỏi gợi mở, không chỉ ra cách sửa).
- Level 2: Conceptual explanation (Giải thích khái niệm/nguyên lý, không đưa code sửa).
- Level 3: Directed hint (Chỉ ra vị trí và hướng thay đổi, tránh đưa toàn bộ code giải).
- Level 4: Explicit solution (Cung cấp mã sửa hoàn chỉnh kèm giải thích mức độ nhập môn).

Quản lý trạng thái phiên học có tính tất định (deterministic session state):
- current_hint_level
- highest_hint_level_used
- solution_revealed
- Chống nhảy cóc tự động từ Level 1 sang Level 4.
"""

from datetime import datetime, timezone
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.tutor_schema import (
    DiagnosisCategory,
    HintLevel,
    TutorDiagnosis,
    TutorResponse,
)


class HintSessionState(BaseModel):
    """Trạng thái tiến trình gợi ý trong một phiên học cụ thể."""

    session_id: str
    current_hint_level: int = Field(default=1, ge=1, le=4)
    highest_hint_level_used: int = Field(default=1, ge=1, le=4)
    solution_revealed: bool = False
    history: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def advance(self, requested_level: Optional[int] = None, allow_jump_to_solution: bool = False) -> int:
        """
        Tiến dần cấp độ gợi ý:
        - Nếu không chỉ định: tăng đều đặn 1 cấp độ (1 -> 2 -> 3 -> 4).
        - Nếu chỉ định requested_level:
          * Chống nhảy cóc: Nếu đang ở Level 1 và yêu cầu Level 4 mà không có allow_jump_to_solution,
            hệ thống sẽ nâng lên Level 2 thay vì nhảy vọt thẳng lên Level 4.
        """
        now = datetime.now(timezone.utc)
        self.updated_at = now

        if requested_level is None:
            new_level = min(4, self.current_hint_level + 1)
        else:
            requested_clamped = max(1, min(4, int(requested_level)))
            # Chống tự động nhảy từ Level 1 lên Level 4
            if self.current_hint_level == 1 and requested_clamped == 4 and not allow_jump_to_solution:
                new_level = 2
            else:
                new_level = requested_clamped

        self.current_hint_level = new_level
        if new_level > self.highest_hint_level_used:
            self.highest_hint_level_used = new_level

        self.solution_revealed = (self.current_hint_level == 4)
        return self.current_hint_level


class HintPayload(BaseModel):
    """Gói dữ liệu gợi ý sư phạm ứng với cấp độ được sinh ra."""

    hint_level: int
    teaching_strategy: str
    tutor_response: str
    next_action: str
    solution_revealed: bool


class HintManager:
    """
    Bộ điều phối gợi ý sư phạm tiến dần cho CodeSense AI Tutor.
    """

    def __init__(self):
        self._sessions: dict[str, HintSessionState] = {}

    def get_or_create_session(
        self,
        session_id: str,
        initial_level: int = 1,
    ) -> HintSessionState:
        """Lấy hoặc tạo mới trạng thái phiên gợi ý."""
        if session_id not in self._sessions:
            clamped_init = max(1, min(4, int(initial_level)))
            state = HintSessionState(
                session_id=session_id,
                current_hint_level=clamped_init,
                highest_hint_level_used=clamped_init,
                solution_revealed=(clamped_init == 4),
            )
            self._sessions[session_id] = state
        return self._sessions[session_id]

    def advance_hint(
        self,
        session_id: str,
        requested_level: Optional[int] = None,
        allow_jump_to_solution: bool = False,
    ) -> HintSessionState:
        """
        Yêu cầu cấp độ gợi ý tiếp theo cho phiên học (deterministic progression).
        """
        session = self.get_or_create_session(session_id)
        session.advance(requested_level=requested_level, allow_jump_to_solution=allow_jump_to_solution)
        return session

    def reset_session(self, session_id: str) -> HintSessionState:
        """Đặt lại phiên học về mức gợi ý ban đầu (Level 1)."""
        session = HintSessionState(session_id=session_id, current_hint_level=1, highest_hint_level_used=1)
        self._sessions[session_id] = session
        return session

    @classmethod
    def validate_pedagogical_safety(
        cls,
        hint_level: int,
        solution_revealed: bool,
    ) -> tuple[bool, str]:
        """
        Kiểm tra an toàn sư phạm:
        Level 1, 2, 3 bắt buộc solution_revealed = False.
        Chỉ Level 4 mới được phép solution_revealed = True.
        """
        if hint_level < 4 and solution_revealed:
            return False, f"Vi phạm sư phạm: Cấp độ gợi ý {hint_level} không được phép tiết lộ giải pháp hoàn chỉnh."
        return True, "Hợp lệ"

    @classmethod
    def generate_progressive_hint(
        cls,
        diagnosis: TutorDiagnosis,
        hint_level: int,
        student_code: Optional[str] = None,
    ) -> HintPayload:
        """
        Sinh nội dung gợi ý tất định tương ứng với chẩn đoán và mức độ yêu cầu (1..4).
        Acceptance:
        - Same diagnosis can produce progressively more explicit help.
        - Level 1-3 do not intentionally reveal complete answer.
        - Level 4 reveals explicit complete code and explanation.
        """
        target_level = max(1, min(4, int(hint_level)))
        issue_type = diagnosis.issue_type
        category = diagnosis.category
        location = diagnosis.location or "trong đoạn mã của bạn"

        # 1. NO_BUG (Mã hợp lệ)
        if category == DiagnosisCategory.NO_BUG:
            return HintPayload(
                hint_level=target_level,
                teaching_strategy="positive_reinforcement",
                tutor_response=(
                    "Mã nguồn của bạn đã hoàn thành chính xác các yêu cầu đề bài và tuân thủ tốt "
                    "các nguyên lý lập trình hướng đối tượng C#."
                ),
                next_action="Thử mở rộng thêm các tính năng nâng cao hoặc tối ưu mã nguồn.",
                solution_revealed=False,
            )

        # 2. INSUFFICIENT_CONTEXT (Mã chưa đủ)
        if category == DiagnosisCategory.INSUFFICIENT_CONTEXT:
            return HintPayload(
                hint_level=target_level,
                teaching_strategy="context_request",
                tutor_response=(
                    "Mã nguồn bạn gửi lên có vẻ chưa hoàn chỉnh hoặc còn thiếu cấu trúc lớp. "
                    "Hãy bổ sung đầy đủ phần thân lớp và các phương thức cần thiết."
                ),
                next_action="Gửi lại mã nguồn hoàn chỉnh với đầy đủ các khối lệnh và dấu ngoặc nhọn.",
                solution_revealed=False,
            )

        # 3. CÁC LỖI CỤ THỂ THEO TAXONOMY
        # Mẫu 1: Parameter / Field Shadowing
        if issue_type == "parameter_field_shadowing" or "shadowing" in issue_type:
            if target_level == 1:
                return HintPayload(
                    hint_level=1,
                    teaching_strategy="socratic_questioning",
                    tutor_response=(
                        f"Quan sát phép gán {location}: khi cả tham số và trường thành viên đều có cùng tên, "
                        "trình biên dịch C# sẽ ưu tiên tham chiếu tới biến nào trước? "
                        "Bạn có nhớ từ khóa nào dùng để phân biệt rõ trường của đối tượng hiện tại không?"
                    ),
                    next_action="Rà soát lại quy tắc phạm vi (scope) của tham số trong constructor.",
                    solution_revealed=False,
                )
            elif target_level == 2:
                return HintPayload(
                    hint_level=2,
                    teaching_strategy="conceptual_explanation",
                    tutor_response=(
                        "Khái niệm Variable Shadowing trong OOP: Khi tham số hàm có cùng tên với biến trường (field) của lớp, "
                        "tham số cục bộ sẽ che khuất trường đó. Nếu viết 'x = x;', C# hiểu là bạn đang gán tham số cục bộ vào chính nó, "
                        "khiến trường của đối tượng không nhận được dữ liệu. Để chỉ định rõ biến trường của thực thể hiện hành, "
                        "C# cung cấp từ khóa 'this'."
                    ),
                    next_action="Tìm hiểu cách sử dụng từ khóa 'this' để truy cập thành viên của thực thể.",
                    solution_revealed=False,
                )
            elif target_level == 3:
                return HintPayload(
                    hint_level=3,
                    teaching_strategy="directed_hint",
                    tutor_response=(
                        f"Chỉ dẫn cụ thể tại {location}: Trong phép gán gán giá trị cho trường, "
                        "hãy thêm tiền tố 'this.' vào biến nằm ở vế bên trái dấu gán '='. "
                        "Ví dụ: vế trái là 'this.tên_trường' còn vế phải là 'tên_tham_số'."
                    ),
                    next_action="Cập nhật lại vế trái của phép gán trong constructor bằng 'this.'.",
                    solution_revealed=False,
                )
            else:  # Level 4
                return HintPayload(
                    hint_level=4,
                    teaching_strategy="explicit_solution",
                    tutor_response=(
                        "Dưới đây là cách sửa hoàn chỉnh và đoạn mã mẫu chuẩn mực:\n\n"
                        "```csharp\n"
                        "// Sửa phép gán trong constructor:\n"
                        "this.name = name;\n"
                        "```\n\n"
                        "Giải thích chi tiết cho người mới học:\n"
                        "- 'this.name' đại diện cho biến trường (field) thuộc về cá thể đối tượng đang được tạo.\n"
                        "- 'name' (bên phải dấu =) đại diện cho tham số truyền vào từ bên ngoài.\n"
                        "Viết 'this.name = name;' giúp C# lưu giá trị tham số vào trường đối tượng một cách chính xác."
                    ),
                    next_action="Sao chép cú pháp 'this.field = param;' vào bài làm và chạy thử nghiệm.",
                    solution_revealed=True,
                )

        # Mẫu 2: Recursive Property Accessor
        if issue_type == "recursive_property_accessor" or "recursive" in issue_type:
            if target_level == 1:
                return HintPayload(
                    hint_level=1,
                    teaching_strategy="socratic_questioning",
                    tutor_response=(
                        f"Quan sát khối getter tại {location}: khi bạn gọi 'return TênThuộcTính;', "
                        "hàm getter sẽ được thực thi như thế nào? Điều này có tạo thành một chu kỳ tự gọi lại chính nó không?"
                    ),
                    next_action="Suy ngẫm về sự khác nhau giữa Thuộc tính (Property) và Biến lưu trữ (Backing Field).",
                    solution_revealed=False,
                )
            elif target_level == 2:
                return HintPayload(
                    hint_level=2,
                    teaching_strategy="conceptual_explanation",
                    tutor_response=(
                        "Nguyên lý Thuộc tính và Backing Field: Thuộc tính (Property) đóng vai trò là cổng truy xuất (getter/setter), "
                        "không tự nó lưu dữ liệu. Nếu trong khối 'get' bạn lại trả về chính Tên Thuộc Tính, nó sẽ gọi đệ quy vô hạn "
                        "dẫn tới ngoại lệ tràn ngăn xếp (StackOverflowException). Ta cần một biến riêng tư (thường đặt tên có tiền tố gạch dưới '_') "
                        "để lưu giữ giá trị thực sự."
                    ),
                    next_action="Tìm hiểu cấu trúc khai báo biến thành viên riêng (backing field).",
                    solution_revealed=False,
                )
            elif target_level == 3:
                field_hint = "ví dụ: 'private decimal _balance;'"
                target_field = "_balance"
                if student_code:
                    import re
                    match = re.search(r"private\s+[A-Za-z0-9_<>\[\]]+\s+(_[A-Za-z0-9_]+)\s*;", student_code)
                    if match:
                        target_field = match.group(1)
                        field_hint = f"sử dụng biến riêng tư '{target_field}' đã khai báo"
                return HintPayload(
                    hint_level=3,
                    teaching_strategy="directed_hint",
                    tutor_response=(
                        f"Chỉ dẫn cụ thể tại {location}: Trong khối getter, hãy sửa câu lệnh return để trả về biến riêng tư "
                        f"lưu trữ (backing field), {field_hint}. Sửa lại thành 'return {target_field};' "
                        "thay vì trả về chính thuộc tính công khai."
                    ),
                    next_action=f"Thay thế tên thuộc tính trong khối return của getter bằng '{target_field}'.",
                    solution_revealed=False,
                )
            else:  # Level 4
                target_field = "_balance"
                prop_name = "Balance"
                prop_type = "decimal"
                if student_code:
                    import re
                    match_field = re.search(r"private\s+([A-Za-z0-9_<>\[\]]+)\s+(_[A-Za-z0-9_]+)\s*;", student_code)
                    match_prop = re.search(r"public\s+([A-Za-z0-9_<>\[\]]+)\s+([A-Za-z0-9_]+)\s*\{", student_code)
                    if match_field:
                        prop_type = match_field.group(1)
                        target_field = match_field.group(2)
                    if match_prop:
                        prop_name = match_prop.group(2)
                        prop_type = match_prop.group(1)

                return HintPayload(
                    hint_level=4,
                    teaching_strategy="explicit_solution",
                    tutor_response=(
                        "Dưới đây là giải pháp hoàn chỉnh với backing field chuẩn C#:\n\n"
                        "```csharp\n"
                        f"private {prop_type} {target_field}; // Backing field riêng tư\n\n"
                        f"public {prop_type} {prop_name}\n"
                        "{\n"
                        f"    get {{ return {target_field}; }} // Trả về backing field, không gọi lại {prop_name}\n"
                        f"    set {{ {target_field} = value; }}\n"
                        "}\n"
                        "```\n\n"
                        "Giải thích chi tiết cho người mới học:\n"
                        f"Thay vì 'return {prop_name};' (tự gọi đệ quy vô tận gây sập chương trình StackOverflowException), "
                        f"ta dùng biến `{target_field}` để lưu giữ giá trị thực sự của đối tượng."
                    ),
                    next_action=f"Cập nhật lại khối getter trả về `{target_field}` và chạy thử nghiệm.",
                    solution_revealed=True,
                )

        # Mẫu 3: Invalid Setter Validation
        if issue_type == "invalid_setter_validation" or "setter" in issue_type:
            if target_level == 1:
                return HintPayload(
                    hint_level=1,
                    teaching_strategy="socratic_questioning",
                    tutor_response=(
                        f"Quan sát khối setter tại {location}: Trong setter của C#, từ khóa nào "
                        "đại diện cho giá trị mới mà người dùng vừa gán vào? Điều kiện if của bạn đang kiểm tra giá trị nào?"
                    ),
                    next_action="Xem lại từ khóa ngầm định trong khối setter của C#.",
                    solution_revealed=False,
                )
            elif target_level == 2:
                return HintPayload(
                    hint_level=2,
                    teaching_strategy="conceptual_explanation",
                    tutor_response=(
                        "Từ khóa 'value' trong Setter: Trong C#, khi ai đó gán 'obj.Prop = 10;', "
                        "giá trị 10 được đưa vào setter thông qua từ khóa ngầm định mang tên 'value'. "
                        "Muốn kiểm tra tính hợp lệ của dữ liệu mới, bạn phải kiểm tra 'value' trước khi lưu vào trường dữ liệu."
                    ),
                    next_action="Tìm hiểu cách hoạt động của từ khóa 'value' trong property setter.",
                    solution_revealed=False,
                )
            elif target_level == 3:
                return HintPayload(
                    hint_level=3,
                    teaching_strategy="directed_hint",
                    tutor_response=(
                        f"Chỉ dẫn cụ thể tại {location}: Sửa điều kiện kiểm tra thành 'if (value >= 0)' "
                        "hoặc 'if (value < 0)', và đảm bảo gán 'value' vào biến backing field sau khi kiểm tra xong."
                    ),
                    next_action="Sử dụng biến 'value' trong biểu thức if và gán kết quả vào backing field.",
                    solution_revealed=False,
                )
            else:  # Level 4
                return HintPayload(
                    hint_level=4,
                    teaching_strategy="explicit_solution",
                    tutor_response=(
                        "Dưới đây là mẫu setter kiểm tra tính hợp lệ chuẩn C#:\n\n"
                        "```csharp\n"
                        "public int Age\n"
                        "{\n"
                        "    get { return _age; }\n"
                        "    set\n"
                        "    {\n"
                        "        if (value < 0)\n"
                        "            _age = 0;\n"
                        "        else\n"
                        "            _age = value;\n"
                        "    }\n"
                        "}\n"
                        "```\n\n"
                        "Giải thích chi tiết cho người mới học:\n"
                        "- 'value' chứa số tuổi người dùng vừa gán vào.\n"
                        "- Ta kiểm tra: nếu 'value < 0' thì chặn lại gán về 0, ngược lại lưu giá trị 'value' vào `_age`."
                    ),
                    next_action="Cập nhật setter với logic kiểm tra từ khóa `value` như trên.",
                    solution_revealed=True,
                )

        # Mẫu 4: Static / Instance Confusion
        if issue_type == "static_instance_confusion" or "static" in issue_type:
            if target_level == 1:
                return HintPayload(
                    hint_level=1,
                    teaching_strategy="socratic_questioning",
                    tutor_response=(
                        f"Quan sát từ khóa 'static' tại {location}: Sự khác nhau giữa một phương thức/trường "
                        "thuộc về cả lớp (class-level) và thuộc về từng đối tượng cụ thể (instance-level) là gì?"
                    ),
                    next_action="Tự đặt câu hỏi: Đối tượng này cần dữ liệu riêng hay chia sẻ chung với mọi đối tượng khác?",
                    solution_revealed=False,
                )
            elif target_level == 2:
                return HintPayload(
                    hint_level=2,
                    teaching_strategy="conceptual_explanation",
                    tutor_response=(
                        "Phân biệt Static và Instance trong C#: Thành viên 'static' thuộc về lớp và dùng chung "
                        "cho toàn bộ chương trình, không gắn với bất kỳ đối tượng cụ thể nào. "
                        "Ngược lại, các thành viên non-static (instance) chứa trạng thái riêng biệt của từng đối tượng cá thể. "
                        "Một phương thức static không thể trực tiếp gọi thành viên instance nếu không khởi tạo đối tượng qua 'new'."
                    ),
                    next_action="Tìm hiểu sự khác biệt giữa lời gọi tĩnh và lời gọi qua thể hiện đối tượng.",
                    solution_revealed=False,
                )
            elif target_level == 3:
                return HintPayload(
                    hint_level=3,
                    teaching_strategy="directed_hint",
                    tutor_response=(
                        f"Chỉ dẫn cụ thể tại {location}: Bỏ từ khóa 'static' nếu đây là thuộc tính riêng của từng đối tượng, "
                        "hoặc trong hàm Main static, hãy khởi tạo một thực thể bằng toán tử 'new' (ví dụ: `var obj = new MyClass();`) "
                        "rồi mới gọi phương thức qua thực thể đó (`obj.Method();`)."
                    ),
                    next_action="Khởi tạo đối tượng qua từ khóa 'new' trước khi gọi phương thức thể hiện.",
                    solution_revealed=False,
                )
            else:  # Level 4
                return HintPayload(
                    hint_level=4,
                    teaching_strategy="explicit_solution",
                    tutor_response=(
                        "Dưới đây là mã sửa hoàn chỉnh để khắc phục lỗi CS0120 / static:\n\n"
                        "```csharp\n"
                        "public static void Main()\n"
                        "{\n"
                        "    Program p = new Program(); // Khởi tạo thực thể đối tượng cụ thể\n"
                        "    p.Greet(); // Gọi phương thức thông qua đối tượng\n"
                        "}\n"
                        "```\n\n"
                        "Giải thích chi tiết cho người mới học:\n"
                        "Hàm `Greet()` là phương thức non-static nên cần một thực thể cụ thể để hoạt động. "
                        "Toán tử `new Program()` tạo ra đối tượng và gán vào biến `p`, từ đó `p.Greet()` thực thi thành công."
                    ),
                    next_action="Thêm bước khởi tạo đối tượng bằng `new` trong hàm Main.",
                    solution_revealed=True,
                )

        # Mẫu Fallback Chung cho mọi lỗi khác
        if target_level == 1:
            return HintPayload(
                hint_level=1,
                teaching_strategy="socratic_questioning",
                tutor_response=(
                    f"Hãy xem xét kỹ dòng lệnh tại {location}. "
                    f"Vấn đề đang liên quan đến '{issue_type}'. "
                    "Theo bạn, mục đích của dòng lệnh này là gì và nó đã hoạt động đúng mong đợi của đề bài chưa?"
                ),
                next_action="Xem xét lại dòng mã và đối chiếu với yêu cầu đề bài.",
                solution_revealed=False,
            )
        elif target_level == 2:
            return HintPayload(
                hint_level=2,
                teaching_strategy="conceptual_explanation",
                tutor_response=(
                    f"Giải thích khái niệm OOP: Vấn đề được xác định thuộc nhóm '{category.value if hasattr(category, 'value') else category}' "
                    f"với lỗi cụ thể là '{issue_type}'. Hãy chú ý đến việc phân tách trách nhiệm và quy tắc cú pháp của C#."
                ),
                next_action="Đọc lại tài liệu liên quan đến cấu trúc lớp và phạm vi truy cập.",
                solution_revealed=False,
            )
        elif target_level == 3:
            return HintPayload(
                hint_level=3,
                teaching_strategy="directed_hint",
                tutor_response=(
                    f"Chỉ dẫn cụ thể tại {location}: Cần sửa lại cú pháp hoặc cấu trúc logic tại vị trí này. "
                    "Hãy chú ý kiểm tra kiểu dữ liệu, các tham số đầu vào và cách gọi phương thức."
                ),
                next_action="Điều chỉnh lại logic tại vị trí lỗi theo hướng dẫn trên.",
                solution_revealed=False,
            )
        else:  # Level 4
            return HintPayload(
                hint_level=4,
                teaching_strategy="explicit_solution",
                tutor_response=(
                    f"Dưới đây là giải pháp cụ thể cho vấn đề '{issue_type}' tại {location}:\n"
                    "Hãy rà soát và điều chỉnh cấu trúc hàm hoặc thuộc tính để đảm bảo tuân thủ cú pháp C# chuẩn mực."
                ),
                next_action="Áp dụng thay đổi và kiểm tra lại với trình biên dịch.",
                solution_revealed=True,
            )
