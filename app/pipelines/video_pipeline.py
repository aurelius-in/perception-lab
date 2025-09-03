from __future__ import annotations

from typing import Generator, Optional


def frames_from_video(path: str, max_frames: Optional[int] = None) -> Generator[bytes, None, None]:
    """Skeleton frame generator: yields no frames for now.
    Replace with cv2.VideoCapture and JPEG bytes.
    """
    _ = (path, max_frames)
    if False:
        yield b""


