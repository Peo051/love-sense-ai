import json

import firebase_admin
from firebase_admin import credentials

from app.core.config import settings


def is_firebase_admin_initialized() -> bool:
    try:
        firebase_admin.get_app()
        return True
    except ValueError:
        return False


def initialize_firebase_admin() -> bool:
    """Khởi tạo Firebase Admin SDK từ biến môi trường, không đọc key từ repo."""
    if is_firebase_admin_initialized():
        return True

    raw_service_account = settings.firebase_service_account_json.strip()
    if not raw_service_account:
        if settings.app_env.strip().lower() == "production":
            raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT_JSON for Firebase Admin.")
        return False

    try:
        service_account = json.loads(raw_service_account)
    except json.JSONDecodeError as exc:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON must be a valid JSON string.") from exc

    firebase_admin.initialize_app(credentials.Certificate(service_account))
    return True
