
<p align="center">
  <img src="assets/pl-ani.gif" alt="PerceptionLab" width="220" />
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
- **Cloud inference adapters** for detectors/segmenters/OCR; local **ByteTrack/Norfair** for tracking.  
- **Compact evaluation** on a small labeled subset: COCO mAP@0.5, mean IoU, IDF1, and OCR accuracy.  
- **Observability by default**: structured JSON logs per frame, Prometheus metrics, and a prewired Grafana dashboard.  
- **One-click PDF report**: pipeline diagram, metrics tables, latency histograms, and three annotated frames.  
- **Fusion viewer**: a single KITTI frame projects LiDAR points onto RGB to verify calibration logic.  
- **Production hygiene**: FastAPI contracts, typed adapters, Docker Compose, CI + unit tests.

> Intentional emphasis on reliability and measurement. The UI exists to visualize outputs and system health.

---

## What it handles

| Need | Where it lives |
|---|---|
| Understand the scene (detect/segment/track/read) | `app/providers/*`, `pipelines/video_pipeline.py`, `tracking/` |
| Operate under time & resource limits | profile configs, timing utilities, Prometheus histograms, FPS chart |
| Integrate multiple modalities | `pipelines/fusion_projection.py` (KITTI LiDAR → camera) |
| Ship services with clear interfaces | FastAPI in `app/services/api.py`, typed adapters and schemas |
| Evaluate consistently | `agents/evaluator.py`, COCO subset, `metrics.json` + plots |
| Keep runs auditable | per-frame JSON logs, run registry, `report.pdf` with provenance |
| Degrade gracefully | adapter retries, fallbacks, anomaly flags in Observability agent |
| Automate hygiene | `.github/workflows/ci.yml`, `tests/` unit tests |
| Prepare for robotics/edge | ROS topic schema stub, ONNX/TensorRT notes, Jetson profile hints |
| Work across cloud vendors | adapters for OCR and inference endpoints (AWS/Azure/GCP/Replicate/HF) |

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
Pick a clip and a profile. Watch boxes, masks, track IDs with short tails, and OCR overlays. A small panel shows FPS and per-stage latency. Expand the latest JSON event to inspect exact outputs.

**Evaluate tab**  
Select the labeled subset and tasks. See mAP@0.5, mean IoU, IDF1, and OCR accuracy with small plots.

**Metrics tab**  
Prometheus metrics are exported by the API. Grafana shows latency histograms and FPS trends.

**Reports tab**  
Generate `runs/<id>/report.pdf`. The report includes provenance, metrics, latency plots, and three annotated frames.

**Fusion tab**  
Visualize a single KITTI frame with LiDAR points projected onto the RGB image.

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
# body: { "image_b64": "...", "profile": "realtime" }
# resp: { "boxes": [...], "masks": [...], "tracks": [...], "ocr": [...], "timings": {...}, "frame_id": int }

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
  provider: gcv               # gcv | azure | textract | replicate:paddleocr
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
