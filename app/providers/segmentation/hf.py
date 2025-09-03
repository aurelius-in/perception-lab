from __future__ import annotations

from typing import List, Any, Dict
import os
import requests


class HfSegmentation:
    def __init__(self, model_id: str) -> None:
        self.model_id = model_id

    def infer(self, image_b64: str) -> List[dict]:
        token = os.getenv("HF_API_TOKEN")
        endpoint = os.getenv("HF_SEG_ENDPOINT")  # optional fully qualified endpoint URL
        if not token or not endpoint:
            return []
        try:
            headers = {"Authorization": f"Bearer {token}"}
            payload: Dict[str, Any] = {"inputs": image_b64}
            resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if not resp.ok:
                return []
            data = resp.json()
            # Expecting a provider-specific schema; normalize to list of mask dicts
            # For now pass through as-is; downstream will ignore if unusable
            if isinstance(data, list):
                return data
            return data.get("masks", []) if isinstance(data, dict) else []
        except Exception:
            return []


