from typing import Dict, List, Any
from pathlib import Path
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from .schemas import DatasetSpec, EvalSpec, ResultCard

# Ingest helpers
try:
    from ingest.pdf.loader import extract_pdf_text
    from ingest.chunking.sectioner import section_by_pages
    from ingest.hashing.hasher import sha256_bytes, sha256_text_norm
except Exception:  # pragma: no cover - optional at runtime
    extract_pdf_text = None  # type: ignore
    section_by_pages = None  # type: ignore
    sha256_bytes = None  # type: ignore
    sha256_text_norm = None  # type: ignore


app = FastAPI(title="PerceptionLab Service", version="1.0.0")

# Optional OpenTelemetry tracing setup
try:  # pragma: no cover - optional
    import os
    from opentelemetry import trace  # type: ignore
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter  # type: ignore
    from opentelemetry.sdk.resources import Resource  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore

    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        resource = Resource.create({"service.name": "perceptionlab-service"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
except Exception:
    pass


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


# Prometheus metrics (optional)
try:  # pragma: no cover - optional at runtime
    from prometheus_client import Counter, Gauge, Histogram, generate_latest  # type: ignore

    METRIC_EVAL_COUNT = Counter("perceptionlab_eval_total", "Number of eval runs")
    METRIC_INGEST_COUNT = Counter("perceptionlab_ingest_total", "Number of ingest requests")
    METRIC_P95_LAT_MS = Gauge("perceptionlab_p95_latency_ms", "Reported p95 latency (ms)")
    METRIC_COST_USD = Gauge("perceptionlab_cost_usd", "Reported cost in USD")
    METRIC_BLOCKED = Counter("perceptionlab_blocked_attempts_total", "Number of blocked attempts")
    METRIC_REQ_LAT = Histogram("perceptionlab_request_ms", "Request latency (ms)")
except Exception:  # pragma: no cover
    METRIC_EVAL_COUNT = None
    METRIC_INGEST_COUNT = None
    METRIC_P95_LAT_MS = None
    METRIC_COST_USD = None
    METRIC_BLOCKED = None
    METRIC_REQ_LAT = None


@app.get("/v1/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/ingest")
def ingest(dataset: DatasetSpec) -> Dict[str, str]:
    try:
        if METRIC_INGEST_COUNT:
            METRIC_INGEST_COUNT.inc()
    except Exception:
        pass
    out_dir = Path("ingest_store") / dataset.dataset_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load simple policies (optional)
    policy = {"max_tokens_per_chunk": 1200}
    pol_path = Path("ingest/policies/rules.yaml")
    if pol_path.exists():
        try:
            import yaml  # type: ignore

            policy = yaml.safe_load(pol_path.read_text(encoding="utf-8")) or policy
        except Exception:
            pass

    # Persist dataset spec
    (out_dir / "dataset.json").write_text(json.dumps(dataset.dict(), indent=2), encoding="utf-8")

    # Process inputs (only local PDFs for now)
    sections_path = out_dir / "sections.jsonl"
    doc_index: List[Dict[str, Any]] = []
    total_chunks = 0

    for uri in dataset.uris:
        p = Path(uri)
        if not p.exists() or p.suffix.lower() != ".pdf":
            continue
        raw_hash = None
        try:
            raw_hash = sha256_bytes(p.read_bytes()) if sha256_bytes else None
        except Exception:
            raw_hash = None

        pages = extract_pdf_text(p) if extract_pdf_text else []
        chunks = section_by_pages(pages, int(policy.get("max_tokens_per_chunk", 1200))) if section_by_pages else []
        # Write chunks as JSONL with normalized text + hash
        with sections_path.open("a", encoding="utf-8") as f:
            for ch in chunks:
                norm, h = ("", "")
                try:
                    norm, h = sha256_text_norm(ch.get("text", "")) if sha256_text_norm else (ch.get("text", ""), "")
                except Exception:
                    norm, h = (ch.get("text", ""), "")
                row = {
                    "doc": str(p.name),
                    "title": ch.get("title", ""),
                    "text": norm,
                    "hash": h,
                }
                f.write(json.dumps(row) + "\n")
                total_chunks += 1
        doc_index.append({"doc": p.name, "raw_sha256": raw_hash, "pages": len(pages), "chunks": len(chunks)})

    (out_dir / "doc_index.json").write_text(json.dumps(doc_index, indent=2), encoding="utf-8")

    return {
        "ok": "true",
        "dataset_id": dataset.dataset_id,
        "path": str(out_dir),
        "docs": len(doc_index),
        "chunks": total_chunks,
    }


@app.post("/v1/eval", response_model=ResultCard)
def eval_run(spec: EvalSpec) -> ResultCard:
    # Stub: return a minimal result card with provenance
    run_id = spec.run_id or "run-local"
    try:
        if METRIC_EVAL_COUNT:
            METRIC_EVAL_COUNT.inc()
    except Exception:
        pass
    return ResultCard(
        run_id=run_id,
        model_name=spec.model_name,
        model_version=spec.model_version,
        metrics={},
        artifacts={},
        doc_hashes=[],
        signature=None,
    )


@app.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    try:
        from prometheus_client import generate_latest  # type: ignore

        return generate_latest().decode("utf-8")
    except Exception:
        return ""

