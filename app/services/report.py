from __future__ import annotations

from pathlib import Path
from weasyprint import HTML
import json
import io
import base64
import matplotlib.pyplot as plt


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

    # Generate a simple latency histogram from events.jsonl if available
    hist_data_uri = ""
    events_path = run_dir / "events.jsonl"
    if events_path.exists():
        latencies = []
        try:
            for line in events_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                obj = json.loads(line)
                t = obj.get("timings", {})
                total = float(t.get("pre", 0.0)) + float(t.get("model", 0.0)) + float(t.get("post", 0.0))
                if total > 0:
                    latencies.append(total)
        except Exception:
            latencies = []
        if latencies:
            fig, ax = plt.subplots(figsize=(4, 2.5), dpi=150)
            ax.hist(latencies, bins=10, color="#02ABC1")
            ax.set_title("Latency (ms)")
            ax.set_xlabel("ms")
            ax.set_ylabel("count")
            buf = io.BytesIO()
            plt.tight_layout()
            fig.savefig(buf, format="png")
            plt.close(fig)
            data = base64.b64encode(buf.getvalue()).decode("utf-8")
            hist_data_uri = f"data:image/png;base64,{data}"

    html = f"""
    <html>
      <head>
        <meta charset='utf-8'/>
        <style>
          body {{ font-family: sans-serif; }}
          h1 {{ color: #02ABC1; }}
          .row {{ display: flex; flex-direction: row; }}
          table {{ border-collapse: collapse; margin: 8px 0; }}
          th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: left; }}
        </style>
      </head>
      <body>
        <h1>PerceptionLab Report</h1>
        <p>Run directory: {run_dir}</p>
        <img src='{(Path.cwd() / 'ui' / 'assets' / 'pipeline.svg').as_posix()}' style='max-width: 90%;'/>
        <h2>Metrics</h2>
        <pre>{json.dumps(metrics_json, indent=2)}</pre>
        <h3>Metrics Table</h3>
        <table>
          <tr><th>Task</th><th>Metric</th><th>Value</th></tr>
          {''.join([
            ''.join([f"<tr><td>{task}</td><td>{mname}</td><td>{val}</td></tr>" for mname, val in (metrics_json.get('metrics', {}).get(task, {}) or {}).items()])
            for task in (metrics_json.get('metrics', {}) or {}).keys()
          ])}
        </table>
        <h3>Confusion Matrix (if available)</h3>
        {"<pre>" + json.dumps(metrics_json.get('cm'), indent=2) + "</pre>" if metrics_json.get('cm') is not None else "<p>Not available.</p>"}
        <h2>Annotated Frames</h2>
        <div class='row'>{img_tags}</div>
        <h2>Latency Histogram</h2>
        {f"<img src='{hist_data_uri}' style='max-width: 60%;'/>" if hist_data_uri else "<p>No events yet.</p>"}
      </body>
    </html>
    """
    report_path = run_dir / "report.pdf"
    HTML(string=html).write_pdf(str(report_path))
    return report_path


