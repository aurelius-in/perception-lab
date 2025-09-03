from __future__ import annotations

from pathlib import Path
from weasyprint import HTML


def build_pdf_report(run_dir: Path) -> Path:
    # Minimal HTML report
    html = f"""
    <html>
      <head>
        <meta charset='utf-8'/>
        <style>
          body {{ font-family: sans-serif; }}
          h1 {{ color: #02ABC1; }}
        </style>
      </head>
      <body>
        <h1>PerceptionLab Report</h1>
        <p>Run directory: {run_dir}</p>
      </body>
    </html>
    """
    report_path = run_dir / "report.pdf"
    HTML(string=html).write_pdf(str(report_path))
    return report_path


