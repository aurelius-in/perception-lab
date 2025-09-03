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
from app.utils.viz import draw_boxes, draw_track_ids, overlay_soft_masks, draw_ocr_labels
from app.utils.timing import StageTimer, timed
from app.providers.tracking.bytetrack import SimpleTracker
from app.providers.segmentation.hf import HfSegmentation


app = FastAPI(title="Perception Ops Lab API", version="0.1.0")

registry = RunRegistry()
metrics = get_metrics_registry()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/run_frame")
def run_frame(req: RunFrameRequest) -> dict:
    # Process a single frame and persist artifacts
    run_id = registry.ensure_run()
    # Minimal provider wiring
    providers = load_providers_config()
    det_cfg = providers.get("detection", {})
    if req.provider_override and isinstance(req.provider_override, dict):
        det_cfg = req.provider_override.get("detection", det_cfg)
    det_provider = det_cfg.get("provider", "replicate")
    det_model = det_cfg.get("model", "ultralytics/yolov8")
    boxes = []
    timer = StageTimer()
    if det_provider == "replicate":
        with timed(timer, "model"):
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

    if img is not None:
        box_tuples = [(b["x1"], b["y1"], b["x2"], b["y2"]) for b in boxes]
        vis = draw_boxes(img, box_tuples) if box_tuples else img.copy()
        # Real segmentation overlay if configured
        try:
            seg = HfSegmentation(model_id="seg")
            masks = seg.infer(req.image_b64)
            # Expect either binary mask arrays or provider-specific; if binary buffers available, overlay
            bin_masks = []
            for m in masks:
                buf = m.get("mask") if isinstance(m, dict) else None
                if buf is not None:
                    import base64 as _b64, numpy as _np
                    raw = _b64.b64decode(buf)
                    arr2 = _np.frombuffer(raw, dtype=_np.uint8)
                    # Fallback shape; real endpoints should include shape metadata
                    try:
                        h, w = vis.shape[:2]
                        bin_masks.append(arr2.reshape(h, w))
                    except Exception:
                        continue
            if bin_masks:
                vis = overlay_soft_masks(vis, bin_masks)
        except Exception:
            pass
        vis = draw_track_ids(vis, tracks)
        # OCR labels placeholder draw (no real OCR yet)
        try:
            vis = draw_ocr_labels(vis, [])
        except Exception:
            pass
        ok, buf = cv2.imencode(".jpg", vis)
        if ok:
            jpg_bytes = buf.tobytes()
            annotated_b64 = base64.b64encode(jpg_bytes).decode("utf-8")
            run_dir = Path("runs") / run_id
            run_dir.mkdir(parents=True, exist_ok=True)
            existing = sorted(run_dir.glob("annotated_*.jpg"))
            if len(existing) < 3:
                next_idx = len(existing)
                out_path = run_dir / f"annotated_{next_idx:03d}.jpg"
                out_path.write_bytes(jpg_bytes)
                annotated_path = str(out_path)

    # Apply overlay filters (class include) if provided
    class_include = None
    if req.overlay_opts and isinstance(req.overlay_opts, dict):
        class_include = req.overlay_opts.get("class_include")
    if class_include:
        boxes = [b for b in boxes if b.get("cls") in class_include]

    # Simple tracking stub
    tracks = SimpleTracker().update(boxes)

    # Export basic metrics
    if "model" in timer.timings_ms:
        metrics.latency_model_ms.observe(timer.timings_ms["model"]) 

    total_ms = sum(timer.timings_ms.values()) or 1e-6
    fps_val = 1000.0 / total_ms

    event = {
        "boxes": boxes,
        "masks": [],
        "tracks": tracks,
        "ocr": [],
        "timings": {
            "model": round(timer.timings_ms.get("model", 0.0), 2),
        },
        "frame_id": 0,
        "run_id": run_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "fps": fps_val,
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
    # Call evaluator agent placeholder and persist
    from app.agents.evaluator import EvaluatorAgent
    run_id = registry.last_run_id() or registry.ensure_run()
    agent = EvaluatorAgent(config={})
    result = agent.evaluate(req.dataset, req.tasks)
    result.update({"run_id": run_id})
    run_dir = Path("runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


@app.post("/report")
def report(req: ReportRequest) -> dict:
    # Build report using report service
    from .report import build_pdf_report
    run_dir = Path("runs") / req.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    path = build_pdf_report(run_dir)
    return {"report_path": str(path)}


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


@app.get("/events_snapshot")
def events_snapshot(limit: int = 50) -> JSONResponse:
    run_id = registry.last_run_id()
    if not run_id:
        return JSONResponse({"run_id": None, "fps": [], "latency_pre": [], "latency_model": [], "latency_post": [], "frame_ids": []})
    path = Path("runs") / run_id / "events.jsonl"
    fps: list[float] = []
    lpre: list[float] = []
    lmod: list[float] = []
    lpost: list[float] = []
    fids: list[int] = []
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
        for line in lines[-limit:]:
            try:
                obj = json.loads(line)
                fids.append(int(obj.get("frame_id", 0)))
                fps.append(float(obj.get("fps", 0.0)))
                t = obj.get("timings", {})
                lpre.append(float(t.get("pre", 0.0)))
                lmod.append(float(t.get("model", 0.0)))
                lpost.append(float(t.get("post", 0.0)))
            except Exception:
                continue
    return JSONResponse({"run_id": run_id, "fps": fps, "latency_pre": lpre, "latency_model": lmod, "latency_post": lpost, "frame_ids": fids})


@app.get("/load_metrics")
def load_metrics(run_id: str | None = None) -> JSONResponse:
    rid = run_id or registry.last_run_id()
    if not rid:
        return JSONResponse({"run_id": None, "metrics": None})
    path = Path("runs") / rid / "metrics.json"
    if not path.exists():
        return JSONResponse({"run_id": rid, "metrics": None})
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        data = None
    return JSONResponse({"run_id": rid, "metrics": data})


@app.post("/export_run")
def export_run(payload: dict) -> dict:
    rid = payload.get("run_id") or registry.last_run_id()
    if not rid:
        return {"zip_path": None, "error": "no run id"}
    run_dir = Path("runs") / rid
    if not run_dir.exists():
        return {"zip_path": None, "error": "run dir not found"}
    import shutil
    zip_base = Path("runs") / f"{rid}_bundle"
    zip_file = shutil.make_archive(str(zip_base), "zip", str(run_dir))
    return {"zip_path": zip_file, "run_id": rid}


