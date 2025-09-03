from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import json


@dataclass
class CocoImage:
    id: int
    file_name: str
    width: int
    height: int


def load_coco(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data


def coco_image_map(data: dict) -> Dict[int, CocoImage]:
    mapping: Dict[int, CocoImage] = {}
    for im in data.get("images", []):
        mapping[int(im["id"]) ] = CocoImage(
            id=int(im["id"]),
            file_name=str(im.get("file_name", "")),
            width=int(im.get("width", 0)),
            height=int(im.get("height", 0)),
        )
    return mapping


def coco_gt_boxes_by_image(data: dict) -> Dict[int, List[Tuple[float, float, float, float]]]:
    by_image: Dict[int, List[Tuple[float, float, float, float]]] = {}
    for ann in data.get("annotations", []):
        img_id = int(ann["image_id"])
        x, y, w, h = ann.get("bbox", [0, 0, 0, 0])
        box = (float(x), float(y), float(x + w), float(y + h))
        by_image.setdefault(img_id, []).append(box)
    return by_image


