from __future__ import annotations

from typing import List


class AwsTextractOcr:
    def __init__(self, region: str | None = None) -> None:
        self.region = region

    def infer(self, image_b64: str) -> List[dict]:
        # Placeholder; integrate with AWS Textract
        return []


