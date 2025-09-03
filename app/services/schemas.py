from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


ProfileName = Literal["realtime", "accuracy"]


class RunFrameRequest(BaseModel):
    image_b64: str
    profile: ProfileName = Field(default="realtime")
    # Optional override of provider/model for showcase flexibility
    provider_override: dict | None = None
    # Optional overlay/threshold options
    overlay_opts: dict | None = None  # {"class_include": [str], "mask_opacity": float, "conf_thresh": float, "nms_iou": float}


class RunVideoRequest(BaseModel):
    video_path: str
    profile: ProfileName = Field(default="realtime")


class EvaluateRequest(BaseModel):
    dataset: str
    tasks: List[Literal["det", "seg", "track", "ocr"]]


class ReportRequest(BaseModel):
    run_id: str


