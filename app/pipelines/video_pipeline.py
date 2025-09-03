from __future__ import annotations

from typing import Generator, Optional

import cv2


def frames_from_video(path: str, max_frames: Optional[int] = None) -> Generator[bytes, None, None]:
    cap = cv2.VideoCapture(path)
    count = 0
    try:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            ok, buf = cv2.imencode('.jpg', frame)
            if not ok:
                break
            yield buf.tobytes()
            count += 1
            if max_frames is not None and count >= max_frames:
                break
    finally:
        cap.release()


