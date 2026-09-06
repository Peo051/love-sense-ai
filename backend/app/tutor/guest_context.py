"""
Guest Context Signer - Cơ chế xác thực ngữ cảnh mật mã không lưu DB cho khách vãng lai (APT-013).

Cung cấp:
- Ký HMAC-SHA256 cho ngữ cảnh học tập của Guest (diagnosis, level, code, session_id).
- Xác thực và chống giả mạo token (anti-tamper protection).
- Ngăn chặn client tự ý reset trạng thái hoặc sửa đổi cấp độ gợi ý.
"""

import base64
import hashlib
import hmac
import json
import time
from typing import Any, Optional

from app.core.config import settings


class GuestContextError(Exception):
    """Lỗi chung liên quan đến ngữ cảnh guest."""
    pass


class GuestContextTamperedError(GuestContextError):
    """Lỗi khi token ngữ cảnh của guest bị giả mạo hoặc chữ ký không hợp lệ."""
    pass


class GuestContextSigner:
    """
    Tiện ích ký và xác thực ngữ cảnh học tập cho chế độ Stateless Guest.
    """

    @classmethod
    def get_secret_key(cls, explicit_key: Optional[str] = None) -> bytes:
        key = explicit_key or getattr(settings, "secret_key", None) or "codesense-ai-tutor-guest-secret-key-2026"
        return key.encode("utf-8")

    @classmethod
    def sign_guest_context(
        cls,
        payload: dict[str, Any],
        secret_key: Optional[str] = None,
    ) -> str:
        """
        Ký mật mã HMAC-SHA256 cho payload ngữ cảnh guest.
        """
        data_to_sign = dict(payload)
        if "timestamp" not in data_to_sign:
            data_to_sign["timestamp"] = int(time.time())

        json_bytes = json.dumps(data_to_sign, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(json_bytes).decode("utf-8")

        key = cls.get_secret_key(secret_key)
        signature = hmac.new(key, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()

        return f"{payload_b64}.{signature}"

    @classmethod
    def verify_guest_context(
        cls,
        token: str,
        secret_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Xác thực chữ ký HMAC và giải mã payload.
        Ném ngoại lệ GuestContextTamperedError nếu token bị chỉnh sửa hoặc sai chữ ký.
        """
        if not token or not token.strip():
            raise GuestContextError("Token ngữ cảnh rỗng.")

        parts = token.strip().split(".")
        if len(parts) != 2:
            raise GuestContextTamperedError("Cấu trúc token không đúng định dạng.")

        payload_b64, signature = parts[0], parts[1]
        key = cls.get_secret_key(secret_key)

        expected_sig = hmac.new(key, payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            raise GuestContextTamperedError("Chữ ký token ngữ cảnh không hợp lệ hoặc đã bị can thiệp.")

        try:
            json_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
            payload = json.loads(json_bytes.decode("utf-8"))
        except Exception as exc:
            raise GuestContextTamperedError(f"Không thể giải mã dữ liệu token: {str(exc)}") from exc

        if not isinstance(payload, dict):
            raise GuestContextTamperedError("Dữ liệu payload phải là một JSON object.")

        return payload
