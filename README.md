
<p align="center">
  <img src="assets/pl-ani.gif" alt="PerceptionLab" width="360" />
</p>

# PerceptionLab

**PerceptionLab** is a Python-first, agentic perception and evaluation stack for real-time detection, segmentation, tracking, OCR, and LiDAR-to-camera fusion. It favors **repeatability, observability, and clear reporting** so perception work can be inspected, compared, and improved without heavy local setup.

## Why this exists

- Perception systems need **fast feedback**. PerceptionLab runs short sequences with consistent configs so changes are measurable rather than anecdotal.  
- Teams need **evidence, not screenshots**. The stack produces metrics, latency distributions, and a compact PDF that captures what happened, how it ran, and with which settings.  
- Environments vary. **Cloud adapters** keep the footprint small while allowing model swaps behind a stable interface.  
- Field issues rarely happen on a developer laptop. **Structured logs + Prometheus/Grafana** make behavior visible and debuggable.

## Highlights

- **Agentic orchestration**: Planner → Curator → Runner → Evaluator → Observability → Reporter. Re-run the same plan and get the same artifacts.  
- **Two operating profiles**: `realtime` for throughput and `accuracy` for fidelity; a UI slider compares outputs frame-for-frame.  
- **Cloud adapters** for detection/segmentation/OCR with provider-agnostic interfaces; local tracking.  
- **Evaluation** on a compact subset: COCO mAP@0.5, mean IoU, IDF1, and OCR accuracy; export to JSON + plots.  
- **Observability first**: structured per-frame logs, Prometheus pre/model/post latency histograms, FPS chart, Grafana dashboard.  
- **One-click PDF**: pipeline diagram, metrics tables, latency histograms, and three annotated frames.  
- **Fusion viewer**: a single KITTI frame projects LiDAR points onto RGB to evidence calibration literacy.  
- **Production hygiene**: clean FastAPI contracts (REST + WebSocket), Docker Compose, CI + tests, typed adapters.

> Intentional emphasis on reliability and measurement. The UI exists to visualize outputs and system health.

---

## What it handles (Capability → Why it matters)

| Capability | Why it matters | Where |
|---|---|---|
| Detection / Segmentation / Tracking / OCR | Understand scenes and act reliably | `app/providers/*`, `pipelines/video_pipeline.py`, tracking stubs |
| Realtime vs Accuracy profiles | Balance latency vs fidelity; compare fairly | `app/configs/profiles/*`, UI compare slider |
| Multi‑modal fusion (LiDAR→RGB) | Evidence calibration literacy and 3D intuition | `pipelines/fusion_projection.py` |
| Clean service contracts | Easier integration, safer changes | FastAPI `app/services/api.py`, schemas |
| Metrics (mAP/IoU/IDF1/OCR) | Evidence over anecdotes; track regressions | `agents/evaluator.py`, `runs/<id>/metrics.json` |
| Observability | Diagnose performance; spot anomalies | structured logs, Prometheus, Grafana |
| Reporting | Shareable, audit‑ready artifacts | `app/services/report.py` → PDF |
| CI/testing | Confidence to change code | `.github/workflows/ci.yml`, `tests/` |
| Cloud adapters | Footprint‑savvy, provider‑agnostic | `app/providers/*`, `app/configs/providers.yaml` |

---

## Architecture

```
[UI (Streamlit or React)]  <->  [FastAPI Perception Service]
         |                                 |
         v                                 v
   Agent Orchestrator (LangGraph/CrewAI) ----> Providers (cloud adapters: detection/seg/ocr/LLM)
         |
         +--> Evaluator (mAP/IoU/IDF1/OCR-acc) -> metrics.json, plots
         +--> Observability (Prometheus + logs) -> Grafana
         +--> Report Writer (HTML->PDF) -> runs/<id>/report.pdf
         +--> Fusion Viewer (KITTI projection)
```

---

## Project structure

```
perceptionlab/
  README.md
  docker-compose.yml
  .github/workflows/ci.yml
  .env.example
  app/
    configs/
      providers.yaml
      profiles/realtime.yaml
      profiles/accuracy.yaml
    agents/
      planner.py
      curator.py
      runner.py
      evaluator.py
      observability.py
      reporter.py
      graph.py
    providers/
      detection/{replicate.py, roboflow.py, hf.py, aws_rekognition.py}
      segmentation/{hf.py}
      ocr/{gcv.py, azure.py, textract.py, replicate_paddleocr.py}
      tracking/{bytetrack.py, norfair.py}
      llm/{bedrock.py, azure_openai.py, openai.py, anthropic.py}
    services/
      api.py          # FastAPI (REST + WebSocket)
      schemas.py
      logging_conf.py
      metrics.py
      storage.py      # run registry
      report.py       # HTML->PDF
    pipelines/
      video_pipeline.py
      fusion_projection.py
      vo_stub.py
    utils/
      viz.py
      io.py
      timing.py
      calib.py
      radar_stub.py
  ui/
    streamlit_app.py  # or /ui/web for React client
  data/
    samples/{day.mp4, night.mp4}
    labels/demo_annotations.json
    kitti_frame/{image.png, points.bin, calib.txt}
  runs/               # generated artifacts
  grafana/
    dashboards/perception.json
  tests/
    test_metrics.py
    test_postprocess.py
    test_api.py
```

---

## Quickstart

### 1) Requirements

- Python 3.11+
- Docker and Docker Compose (recommended)
- API keys for any cloud providers you choose

### 2) Environment

```bash
cp .env.example .env
```

Fill only the providers you plan to use:

```
REPLICATE_API_TOKEN=
ROBOFLOW_API_KEY=
HF_API_TOKEN=
GOOGLE_APPLICATION_CREDENTIALS=/app/creds/gcp.json
AZURE_VISION_ENDPOINT=
AZURE_VISION_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
BEDROCK_REGION=
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
```

### 3) Configure adapters and profiles

- `app/configs/providers.yaml` selects detection/seg/OCR providers and models  
- `app/configs/profiles/{realtime.yaml,accuracy.yaml}` define thresholds and rendering

### 4) Minimal data pack

```
data/
  samples/day.mp4
  samples/night.mp4
  labels/demo_annotations.json         # ~40–50 labeled frames, COCO style
  kitti_frame/{image.png, points.bin, calib.txt}   # single-frame fusion
```

Use open sources (BDD100K, Cityscapes, KITTI, nuScenes mini, CARLA). Only include content you’re allowed to use.

### 5) Run with Docker Compose

```bash
docker compose up --build
```

- UI → http://localhost:8501  
- API → http://localhost:8000  
- Prometheus → http://localhost:9090  
- Grafana → http://localhost:3000

### 6) Local run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.services.api:app --host 0.0.0.0 --port 8000
streamlit run ui/streamlit_app.py --server.port 8501
```

---

## Using PerceptionLab

**Run tab**  
Pick a clip and a profile. Watch boxes, soft masks, track IDs with comet tails, and OCR labels. Toggle overlays, filter classes, adjust mask opacity, confidence and NMS. A HUD shows FPS and per‑stage latency; the event log is one click away. Use provider overrides for single‑frame detection, and export side‑by‑side via the compare slider.

**Evaluate tab**  
Select the labeled subset and tasks. See mAP@0.5, mean IoU, IDF1, and OCR accuracy with small plots.

**Metrics tab**  
Prometheus metrics are exported by the API. Built‑in mini‑charts show FPS and per‑stage latencies; Grafana provides richer dashboards.

**Reports tab**  
Generate `runs/<id>/report.pdf`. The report includes a pipeline diagram, provenance table, metrics, latency histograms, and three annotated frames. Quick links show where to download `events.jsonl` and `metrics.json`.

**Fusion tab**  
Visualize a single KITTI frame with LiDAR points projected onto the RGB image.

**Interview mode**  
A 2‑minute sequence that: runs realtime briefly, prompts a realtime vs accuracy comparison, surfaces telemetry, and generates a PDF for the latest run with success toasts.

---

## Agentic workflow

- **PlannerAgent** reads configs and drafts a `run_plan.json`  
- **DataCuratorAgent** validates inputs and emits a `data_manifest.json`  
- **RunnerAgent** executes the pipeline frame-by-frame and writes structured logs  
- **EvaluatorAgent** computes metrics and saves `metrics.json` + plots  
- **ObservabilityAgent** exports Prometheus metrics and flags anomalies  
- **ReportAgent** compiles a compact PDF with provenance and visuals

---

## API contracts

```http
POST /run_frame
# body: { "image_b64": "...", "profile": "realtime", "provider_override": {...}, "overlay_opts": {...} }
# resp: { "boxes": [...], "masks": [...], "tracks": [...], "ocr": [...], "timings": {...}, "frame_id": int, "annotated_path": str, "annotated_b64": str }

POST /run_video
# body: { "video_path": "data/samples/day.mp4", "profile": "realtime" }
# resp: websocket stream of per-frame results; server persists overlays and logs

POST /evaluate
# body: { "dataset": "data/labels/demo_annotations.json", "tasks": ["det","seg","track","ocr"] }
# resp: { "metrics": {"det": {...}, "seg": {...}, ...}, "plots": ["path1","path2"] }

POST /report
# body: { "run_id": "YYYY-MM-DD_HH-MM-SS" }
# resp: { "report_path": "runs/<id>/report.pdf" }
```

**Per-frame log schema (JSON)**

```json
{
  "run_id": "YYYY-MM-DD_HH-MM-SS",
  "frame_id": 123,
  "ts": "2025-09-02T12:34:56.789Z",
  "latency_ms": { "pre": 4.2, "model": 28.5, "post": 6.1 },
  "fps": 22.5,
  "boxes": [{ "x1": 0, "y1": 0, "x2": 10, "y2": 10, "score": 0.9, "cls": "car" }],
  "tracks": [{ "id": 7, "cls": "car", "x1": 0, "y1": 0, "x2": 10, "y2": 10, "trail": [[5,5],[7,7]] }],
  "masks": ["rle_or_poly"],
  "ocr": [{ "text": "STOP", "box": [0,0,10,10] }],
  "provider_provenance": { "detector": "replicate:yolov8", "ocr": "gcv" },
  "errors": []
}
```

---

## Configuration

**`app/configs/providers.yaml`**

```yaml
detection:
  provider: replicate         # replicate | roboflow | hf | aws_rekognition
  model: "ultralytics/yolov8" # provider-specific
  concurrency: 2
segmentation:
  provider: hf
  model: "nvidia/segformer-b0-finetuned-ade-512-512"
ocr:
  provider: replicate         # replicate:paddleocr (set version) | gcv | azure | textract
  version: "paddleocr-version-hash"
tracking:
  provider: bytetrack         # local CPU-friendly tracking
llm_notes:
  provider: bedrock           # or azure_openai | openai | anthropic
```

**`app/configs/profiles/realtime.yaml`**

```yaml
input_size: 640
confidence_thresh: 0.35
nms_iou: 0.5
max_fps: 24
render:
  show_boxes: true
  show_masks: true
  show_tracks: true
  show_ocr: true
```

**`app/configs/profiles/accuracy.yaml`**

```yaml
input_size: 1024
confidence_thresh: 0.25
nms_iou: 0.6
max_fps: 12
render:
  show_boxes: true
  show_masks: true
  show_tracks: true
  show_ocr: true
```

---

## Testing and CI

```bash
pytest -q
```

A GitHub Actions workflow runs lint, type checks, and unit tests on push and pull requests.

---

## Extending PerceptionLab

- Implement an adapter to add a new detector or segmenter  
- Swap OCR providers in `providers.yaml` without touching the pipeline  
- Expose internal models behind the same contract to compare outputs fairly  
- Expand the labeled subset to increase metric fidelity  
- Replace the Streamlit UI with a React client that calls the same contracts

---

## Interview mode (turnkey walkthrough)

Click “Interview Mode” in the Run tab. The sequence loads the curated clip, runs realtime for a few seconds, prompts a realtime vs accuracy comparison, opens telemetry, and builds the PDF. On‑screen captions announce each step; the flow is resilient to transient provider delays.

---

## Data preparation (tiny and legal)

---

## Use Cases (pre‑packaged screens)

- Roadway Traffic & Sign Intelligence: filter to signs/lights, extract OCR, and compare profiles.
- Warehouse Safety & PPE: draw safety zones; count people in‑zone.
- Retail Shelf QA (OCR): extract price/label text and download CSV.
- Smart City Anomaly & Flow: live FPS/latency charts and spike frames.
- Agriculture Field Scan: vegetation heat overlay and obstacle highlight.

---

## Provider keys for segmentation/OCR

- Segmentation (HF endpoint): set `HF_API_TOKEN` and `HF_SEG_ENDPOINT` for real masks; otherwise, soft masks derive from boxes for visualization.
- OCR (Replicate PaddleOCR): set `REPLICATE_API_TOKEN` and a `version` in `providers.yaml`.

PerceptionLab expects two 10–15 s clips and a small COCO labels file. To trim videos locally with ffmpeg:

```bash
ffmpeg -ss 00:00:03 -i source.mp4 -t 00:00:12 -c copy data/samples/day.mp4
ffmpeg -ss 00:00:08 -i source_night.mp4 -t 00:00:12 -c copy data/samples/night.mp4
```

Do not download large datasets automatically; prefer small, permitted samples (e.g., BDD100K, Cityscapes, KITTI, nuScenes mini, CARLA renders).

---

## Roadmap

- ROS bridge publisher and minimal subscriber example  
- ONNX export and TensorRT acceleration toggle  
- Jetson-tuned profile with memory and FPS caps  
- Visual odometry example with configurable trajectories  
- Radar overlay option using a compact CSV format

---

## License

MIT. See `LICENSE` for details.

---

## Acknowledgments

COCO API, ByteTrack, SegFormer/DeepLab, PaddleOCR, Prometheus, Grafana, and open research datasets (KITTI, BDD100K, Cityscapes, nuScenes mini, CARLA).
