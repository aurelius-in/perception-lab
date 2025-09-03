from __future__ import annotations

from pathlib import Path


class EvaluatorAgent:
    def __init__(self, config: dict) -> None:
        self.config = config

    def evaluate(self, dataset_path: str, tasks: list[str]) -> dict:
        # Placeholder IoU and mAP computation outlines using utils.metrics
        from app.utils.metrics import iou_xyxy, map50_placeholder  # noqa: F401
        from app.utils.coco import load_coco, coco_gt_boxes_by_image
        data = load_coco(dataset_path) if Path(dataset_path).exists() else {"images": [], "annotations": []}
        gt_by_img = coco_gt_boxes_by_image(data)
        # No actual preds; return zeros as placeholders
        iou = 0.0 if "seg" in tasks else None
        map50 = 0.0 if "det" in tasks else None
        idf1 = 0.0 if "track" in tasks else None
        ocr_acc = 0.0 if "ocr" in tasks else None
        # Confusion matrix placeholder (2x2) per-class aggregation could go here
        cm = [[0, 0], [0, 0]] if "det" in tasks else None
        metrics = {
            "det": {"map50": map50} if map50 is not None else {},
            "seg": {"miou": iou} if iou is not None else {},
            "track": {"idf1": idf1} if idf1 is not None else {},
            "ocr": {"acc": ocr_acc} if ocr_acc is not None else {},
        }
        return {"dataset": dataset_path, "tasks": tasks, "metrics": metrics, "cm": cm}


