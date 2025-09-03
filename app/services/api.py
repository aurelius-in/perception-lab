from __future__ import annotations

from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
import json
from datetime import datetime, timezone
import base64
from pathlib import Path
import numpy as np
import cv2

from .schemas import EvaluateRequest, ReportRequest, RunFrameRequest, RunVideoRequest
from .metrics import get_metrics_registry
from .storage import RunRegistry
from app.utils.config import load_providers_config
from app.providers.detection.replicate import ReplicateDetector
from app.utils.viz import draw_boxes


app = FastAPI(title="Perception Ops Lab API", version="0.1.0")

registry = RunRegistry()
metrics = get_metrics_registry()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run_frame")
def run_frame(req: RunFrameRequest) -> dict:
    # Stub response matching contract shape
    run_id = registry.ensure_run()
    # Minimal provider wiring
    providers = load_providers_config()
    det_cfg = providers.get("detection", {})
    det_provider = det_cfg.get("provider", "replicate")
    det_model = det_cfg.get("model", "ultralytics/yolov8")
    boxes = []
    if det_provider == "replicate":
        det = ReplicateDetector(det_model)
        boxes = [
            {
                "x1": d.x1,
                "y1": d.y1,
                "x2": d.x2,
                "y2": d.y2,
                "score": d.score,
                "cls": d.cls,
            }
            for d in det.infer(req.image_b64)
        ]

    # Decode input and produce annotated overlay if possible
    annotated_b64 = None
    annotated_path = None
    try:
        img_bytes = base64.b64decode(req.image_b64.encode("utf-8"))
        arr = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        img = None

    if img is not None and len(boxes) > 0:
        box_tuples = [(b["x1"], b["y1"], b["x2"], b["y2"]) for b in boxes]
        vis = draw_boxes(img, box_tuples)
        ok, buf = cv2.imencode(".jpg", vis)
        if ok:
            jpg_bytes = buf.tobytes()
            annotated_b64 = base64.b64encode(jpg_bytes).decode("utf-8")
            out_path = Path("runs") / run_id / f"annotated_{0:03d}.jpg"
            out_path.write_bytes(jpg_bytes)
            annotated_path = str(out_path)

    event = {
        "boxes": boxes,
        "masks": [],
        "tracks": [],
        "ocr": [],
        "timings": {"pre": 0.0, "model": 0.0, "post": 0.0},
        "frame_id": 0,
        "run_id": run_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "fps": 0.0,
        "provider_provenance": {"detector": f"replicate:{det_model}", "ocr": "gcv"},
        "errors": [],
        "annotated_path": annotated_path,
        "annotated_b64": annotated_b64,
    }
    registry.append_event(run_id, json.dumps(event))
    return event


@app.post("/run_video")
def run_video(req: RunVideoRequest) -> JSONResponse:
    # WebSocket stream is planned; acknowledge request for now
    run_id = registry.ensure_run()
    return JSONResponse({"status": "accepted", "run_id": run_id, "note": "WS stream TBD"})


@app.post("/evaluate")
def evaluate(req: EvaluateRequest) -> dict:
    # Minimal stub metrics
    return {
        "metrics": {
            "det": {"map50": 0.0},
            "seg": {"miou": 0.0},
            "track": {"idf1": 0.0},
            "ocr": {"acc": 0.0},
        },
        "plots": [],
    }


@app.post("/report")
def report(req: ReportRequest) -> dict:
    # Stub report path
    return {"report_path": f"runs/{req.run_id}/report.pdf"}


@app.get("/metrics")
def prometheus_metrics() -> Response:
    content, content_type = metrics.export_prometheus_text()
    return PlainTextResponse(content=content, media_type=content_type)


@app.get("/last_event")
def last_event() -> JSONResponse:
    run_id = registry.last_run_id()
    if not run_id:
        return JSONResponse({"run_id": None, "event": None})
    evt = registry.read_last_event(run_id)
    try:
        parsed = json.loads(evt) if evt else None
    except Exception:
        parsed = evt
    return JSONResponse({"run_id": run_id, "event": parsed})


@app.websocket("/ws/run_video")
async def ws_run_video(ws: WebSocket) -> None:
    await ws.accept()
    try:
        params = dict(ws.query_params)
        video_path = params.get("video_path", "data/samples/day.mp4")
        profile = params.get("profile", "realtime")
        run_id = registry.ensure_run()
        # Send a few stub frames with timings/ids
        for i in range(3):
            event = {
                "run_id": run_id,
                "frame_id": i,
                "ts": datetime.now(timezone.utc).isoformat(),
                "timings": {"pre": 2.0, "model": 15.0, "post": 3.0},
                "fps": 20.0,
                "boxes": [],
                "tracks": [],
                "masks": [],
                "ocr": [],
                "provider_provenance": {"detector": "replicate:yolov8", "ocr": "gcv"},
                "note": f"stub stream for {video_path} ({profile})",
                "errors": [],
            }
            registry.append_event(run_id, json.dumps(event))
            metrics.fps.set(event["fps"])  # basic metric update
            await ws.send_json(event)
        await ws.close()
    except WebSocketDisconnect:
        # Client disconnected early
        return


