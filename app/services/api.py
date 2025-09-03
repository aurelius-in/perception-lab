from __future__ import annotations

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from .schemas import EvaluateRequest, ReportRequest, RunFrameRequest, RunVideoRequest
from .metrics import get_metrics_registry
from .storage import RunRegistry


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
    return {
        "boxes": [],
        "masks": [],
        "tracks": [],
        "ocr": [],
        "timings": {"pre": 0.0, "model": 0.0, "post": 0.0},
        "frame_id": 0,
        "run_id": run_id,
    }


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


