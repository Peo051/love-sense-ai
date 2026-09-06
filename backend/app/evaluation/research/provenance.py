"""
Research Provenance & Run Manifest Generator (APT-054).

Nhiệm vụ:
- Ghi nhận nguồn gốc thực nghiệm bất biến (provenance tracking).
- Tạo SHA256 hashes cho dataset, split và cấu hình thực nghiệm.
- Tuyệt đối không ghi nhận API keys hay secrets vào manifest hoặc logs.
"""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def get_git_commit() -> str:
    """Lấy commit hash hiện tại của repository một cách an toàn."""
    try:
        res = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "unknown_commit"


def compute_dataset_hashes(samples: List[Dict[str, Any]], split_samples: List[Dict[str, Any]]) -> tuple[str, str]:
    """Tính toán SHA256 cho toàn bộ dataset và cho split thực nghiệm."""
    full_dump = "\n".join(json.dumps(s, sort_keys=True) for s in samples)
    dataset_hash = hashlib.sha256(full_dump.encode("utf-8")).hexdigest()

    split_dump = "\n".join(json.dumps(s, sort_keys=True) for s in split_samples)
    split_hash = hashlib.sha256(split_dump.encode("utf-8")).hexdigest()

    return dataset_hash, split_hash


def create_research_manifest(
    *,
    run_id: str,
    system: str,
    system_description: str,
    model: str,
    provider: str,
    prompt_version: str,
    dataset_path: Path,
    dataset_hash: str,
    split: str,
    split_hash: str,
    total_samples: int,
    seed: int,
    execution_duration_sec: float,
    temperature: float,
    max_output_tokens: int = 1024,
    extra_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Tạo cấu trúc manifest bất biến (immutable run manifest) cho nghiên cứu thực nghiệm.
    Bảo đảm không có trường mock_mode và không chứa bất kỳ secret nào.
    """
    manifest: Dict[str, Any] = {
        "run_id": run_id,
        "system": system,
        "system_description": system_description,
        "model": model,
        "provider": provider,
        "prompt_version": prompt_version,
        "dataset_version": "1.0.0",
        "dataset_path": str(dataset_path),
        "dataset_hash": dataset_hash,
        "split": split,
        "split_hash": split_hash,
        "total_samples": total_samples,
        "random_seed": seed,
        "git_commit": get_git_commit(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "execution_duration_sec": round(execution_duration_sec, 2),
        "config": {
            "temperature": temperature,
            "top_p": 0.95,
            "max_output_tokens": max_output_tokens,
            **(extra_config or {})
        }
    }
    return manifest
