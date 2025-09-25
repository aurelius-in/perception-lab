from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import DatasetSpec, EvalSpec, ResultCard


app = FastAPI(title="PerceptionLab Service", version="1.0.0")


origins = []
try:
    import os

    origins_raw = os.environ.get("CORS_ALLOW_ORIGINS", "")
    if origins_raw:
        origins = [o.strip() for o in origins_raw.split(",") if o.strip()]
except Exception:
    origins = []

if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/v1/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ingest")
def ingest(dataset: DatasetSpec) -> Dict[str, str]:
    # Stub: accept and acknowledge dataset registration
    return {"ok": "true", "dataset_id": dataset.dataset_id}


@app.post("/v1/eval", response_model=ResultCard)
def eval_run(spec: EvalSpec) -> ResultCard:
    # Stub: return a minimal result card with provenance
    run_id = spec.run_id or "run-local"
    return ResultCard(
        run_id=run_id,
        model_name=spec.model_name,
        model_version=spec.model_version,
        metrics={},
        artifacts={},
        doc_hashes=[],
        signature=None,
    )


