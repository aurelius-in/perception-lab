from __future__ import annotations

from pathlib import Path
from weasyprint import HTML
import json


def build_pdf_report(run_dir: Path) -> Path:
    # Minimal HTML report with up to three annotated frames and metrics snapshot
    metrics_path = run_dir / "metrics.json"
    metrics_json = {}
    if metrics_path.exists():
        try:
            metrics_json = json.loads(metrics_path.read_text(encoding="utf-8"))
        except Exception:
            metrics_json = {}

    images = sorted(run_dir.glob("annotated_*.jpg"))[:3]
    img_tags = "".join([f"<img src='{p.as_posix()}' style='max-width: 32%; margin-right: 4px;'/>" for p in images])

    html = f"""
    <html>
      <head>
        <meta charset='utf-8'/>
        <style>
          body {{ font-family: sans-serif; }}
          h1 {{ color: #02ABC1; }}
          .row {{ display: flex; flex-direction: row; }}
        </style>
      </head>
      <body>
        <h1>PerceptionLab Report</h1>
        <p>Run directory: {run_dir}</p>
        <h2>Metrics</h2>
        <pre>{json.dumps(metrics_json, indent=2)}</pre>
        <h2>Annotated Frames</h2>
        <div class='row'>{img_tags}</div>
      </body>
    </html>
    """
    report_path = run_dir / "report.pdf"
    HTML(string=html).write_pdf(str(report_path))
    return report_path


