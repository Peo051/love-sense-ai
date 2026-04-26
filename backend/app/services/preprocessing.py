import re


def preprocess_text(text: str) -> str:
    """Chuẩn hóa nhẹ nhưng vẫn giữ cấu trúc nhiều dòng của đoạn chat."""
    lines = []

    for line in text.splitlines():
        normalized_line = re.sub(r"\s+", " ", line).strip()
        if normalized_line:
            lines.append(normalized_line)

    return "\n".join(lines)


def normalize_vietnamese(text: str) -> str:
    """Normalize Vietnamese text."""
    return text
