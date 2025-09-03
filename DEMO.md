# PerceptionLab — 8-Minute Runbook

1) Setup
- Start services: `docker compose up --build`
- Open UI: http://localhost:8501
- Ensure API keys if using cloud providers (optional)

2) Run (Realtime)
- Select `day.mp4`, profile `realtime`
- Click Start; show WS events and FPS in Run tab
- Upload a single image under "Single-frame detection" and run `/run_frame`
- Show annotated overlay and response JSON

3) Compare Profiles
- Use "Realtime vs Accuracy" compare; upload one image once and run
- Show side-by-side annotated images

4) Metrics
- Open Metrics tab
- Fetch `/metrics` and show Prometheus text
- Fetch Last JSON event

5) Evaluate
- Switch to Evaluate tab; dataset `data/labels/demo_annotations.json`
- Select tasks (e.g., det)
- Run Eval; show placeholder metrics and confirm `runs/<id>/metrics.json`

6) Report
- Go to Reports tab
- Click "Generate report for last run"; open the printed path
- Show PDF with metrics table, annotated thumbnails, and latency histogram

7) Fusion (stub)
- Open Fusion tab; briefly describe KITTI projection utility

8) Close
- Highlight modular adapters, CI, logging, and how to plug internal models
