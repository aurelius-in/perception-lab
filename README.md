
# PerceptionLab

**PerceptionLab** is a Python-first, agentic perception and evaluation stack for real-time detection, segmentation, tracking, OCR, and LiDAR-to-camera fusion. It provides cloud inference adapters, FastAPI services, structured logging, Prometheus/Grafana observability, COCO-style metrics, and one-click PDF reporting. Built to showcase backend engineering, reliability, and production readiness.

## Highlights

- **Agentic orchestration** with a Planner → Curator → Runner → Evaluator → Observability → Reporter workflow  
- **Real-time pipelines** with two profiles: `realtime` and `accuracy`  
- **Cloud adapters** for detectors, segmenters, and OCR to keep local footprint small  
- **Tracking** with ByteTrack or Norfair using detector outputs  
- **Evaluation** on a compact labeled subset: mAP@0.5, mean IoU, IDF1, OCR accuracy  
- **Observability** via structured JSON logs, Prometheus metrics, and a Grafana dashboard  
- **Reporting** through a PDF artifact including latency plots, metrics tables, and annotated frames  
- **Fusion viewer** renders a single KITTI frame projected from LiDAR to RGB  
- **Production hygiene**: Docker Compose, CI + tests, typed interfaces, clean configs

> Intentional emphasis on backend engineering and architecture. The UI exists to visualize outputs and system health.

---

## Skills Coverage (mapped to typical Perception CV/ML roles)

| Capability sought | Where it lives in PerceptionLab |
|---|---|
| Detection, segmentation, tracking, OCR | `app/providers/*`, `pipelines/video_pipeline.py`, `tracking/` |
| Real-time constraints, performance | Profiles, timing utilities, Prometheus histograms, FPS chart |
| Multi-sensor awareness | `pipelines/fusion_projection.py` (KITTI LiDAR → camera) |
| Python services, clean interfaces | FastAPI in `app/services/api.py`, typed adapters |
| Data & evaluation pipeline | `agents/evaluator.py`, COCO subset, metrics JSON + plots |
| Logging, auditability | JSON logs per frame, run registry, `report.pdf` |
| Error handling, recovery | Adapter retries, fallbacks, anomaly flags |
| CI/CD & testing | `.github/workflows/ci.yml`, `tests/` unit tests |
| ROS, edge readiness | ROS topic schema stub, TensorRT/Jetson notes, ONNX toggle |
| Cloud (AWS/Azure/GCP) | OCR and LLM notes adapters, detection/seg endpoints |

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

## Project Structure

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

Copy and edit env vars:

```bash
cp .env.example .env
```

`.env.example` includes optional keys:

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

### 3) Configure providers and profiles

Edit `app/configs/providers.yaml` to select adapters and models.  
Edit `app/configs/profiles/{realtime.yaml,accuracy.yaml}` for thresholds and rendering.

### 4) Data setup

Prepare two short clips and a tiny labeled subset:

```
data/
  samples/day.mp4
  samples/night.mp4
  labels/demo_annotations.json         # ~40–50 labeled frames, COCO style
  kitti_frame/{image.png, points.bin, calib.txt}   # single-frame fusion
```

> Use open driving datasets like BDD100K, Cityscapes, KITTI, nuScenes mini, or CARLA renders. Only include content you are permitted to use.

### 5) Run with Docker Compose

```bash
docker compose up --build
```

- UI at http://localhost:8501  
- API at http://localhost:8000  
- Prometheus at http://localhost:9090  
- Grafana at http://localhost:3000

### 6) Local run (without Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.services.api:app --host 0.0.0.0 --port 8000
streamlit run ui/streamlit_app.py --server.port 8501
```

---

## Using PerceptionLab

### Run tab

- Select `day.mp4` or `night.mp4` and a profile `realtime` or `accuracy`
- Start processing to see boxes, masks, track IDs with short “comet tails” and OCR overlays
- A mini panel shows FPS and per-stage latency
- An expander reveals the last structured JSON event

### Evaluate tab

- Choose the labeled COCO subset and tasks to evaluate  
- View mAP@0.5, mean IoU, IDF1, OCR accuracy with small plots

### Metrics tab

- Prometheus metrics are exported by the API  
- Open Grafana to view latency histograms and FPS trends

### Reports tab

- Click Generate to create `runs/<id>/report.pdf`  
- The report includes metrics tables, latency plots, and three annotated frames

### Fusion tab

- Visualize a single KITTI frame with LiDAR points projected to the RGB image

---

## Agentic Workflow

- **PlannerAgent** reads configs and produces a `run_plan.json`  
- **DataCuratorAgent** validates presence of clips and labels and prepares a `data_manifest.json`  
- **RunnerAgent** executes the pipeline frame by frame and writes structured logs  
- **EvaluatorAgent** computes metrics and saves `metrics.json` and plots  
- **ObservabilityAgent** exports Prometheus metrics and flags anomalies  
- **ReportAgent** compiles a PDF with provenance, metrics, plots, and annotated frames

---

## API Contracts

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

Run tests:

```bash
pytest -q
```

A GitHub Actions workflow runs lint, type checks, and unit tests on push and pull requests.

---

## Extending PerceptionLab

- Add a new detector or segmenter by implementing the provider adapter interface  
- Swap OCR providers in `providers.yaml`  
- Connect internal models by exposing them behind the same adapter contract  
- Expand the labeled subset to refine metric fidelity  
- Replace the UI with a React client that calls the same FastAPI contracts

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

- COCO API, ByteTrack, SegFormer/DeepLab, PaddleOCR  
- Prometheus and Grafana  
- KITTI, BDD100K, Cityscapes, nuScenes mini, and CARLA for publicly available research data

---

**GitHub Topics**  
`computer-vision` `perception` `agentic-ai` `langgraph` `fastapi` `docker-compose` `prometheus` `grafana` `coco` `object-detection` `segmentation` `tracking` `ocr` `sensor-fusion` `lidar` `ros` `onnx` `tensorrt` `aws` `azure` `gcp` `replicate` `huggingface` `evaluation` `observability` `logging`
