from __future__ import annotations

from typing import List


class AzureVisionOcr:
    def __init__(self, endpoint: str | None = None, key: str | None = None) -> None:
        self.endpoint = endpoint
        self.key = key

    def infer(self, image_b64: str) -> List[dict]:
        # Placeholder; integrate with Azure Computer Vision Read API
        return []


