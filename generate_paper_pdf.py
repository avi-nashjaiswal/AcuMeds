"""
AcuMeds IEEE Research Paper Generator
Reads AcuMeds_AI_Medical_IEEE_Paper.html, dynamically adjusts typography and spacing
to calibrate the manuscript to exactly 9 pages, and compiles it via Edge headless.
"""

import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "AcuMeds_AI_Medical_IEEE_Paper.html"
PDF_PATH = ROOT / "AcuMeds_AI_Medical_IEEE_Paper.pdf"
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def get_page_count():
    if not PDF_PATH.exists():
        return 0
    with open(PDF_PATH, "rb") as f:
        data = f.read()
    return len(re.findall(rb'/Type\s*/Page\b', data))

def compile_pdf():
    cmd = [
        EDGE_BIN,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        f"file:///{HTML_PATH}"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.returncode == 0

def update_css_parameters(margin_in, font_pt, line_h, col_gap_in):
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace @page margin
    content = re.sub(
        r'margin:\s*[0-9.]+in\s*[0-9.]+in\s*[0-9.]+in\s*[0-9.]+in;',
        f'margin: {margin_in:.2f}in {margin_in*0.85:.2f}in {margin_in:.2f}in {margin_in*0.85:.2f}in;',
        content
    )

    # Replace body font-size and line-height
    content = re.sub(
        r'font-size:\s*[0-9.]+pt;\s*line-height:\s*[0-9.]+;',
        f'font-size: {font_pt:.2f}pt;\n    line-height: {line_h:.2f};',
        content,
        count=1
    )

    # Replace two-column column-gap
    content = re.sub(
        r'column-gap:\s*[0-9.]+in;',
        f'column-gap: {col_gap_in:.2f}in;',
        content
    )

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("=== Calibrating AcuMeds IEEE Paper to EXACTLY 9 Pages ===")
    
    # Read current state
    compile_pdf()
    current_pages = get_page_count()
    print(f"Starting PDF page count: {current_pages}")

    # Parameter grid for calibration
    configs = [
        # (margin, font_pt, line_height, col_gap)
        (0.60, 9.30, 1.16, 0.20),
        (0.65, 9.60, 1.20, 0.22),
        (0.70, 9.80, 1.24, 0.24),
        (0.75, 10.00, 1.28, 0.25),
        (0.80, 10.20, 1.30, 0.26),
        (0.85, 10.40, 1.32, 0.28),
        (0.68, 9.70, 1.22, 0.23),
        (0.72, 9.90, 1.26, 0.24),
        (0.74, 9.95, 1.27, 0.25)
    ]

    for margin, font, lh, gap in configs:
        print(f"Testing config: Margin={margin:.2f}in, Font={font:.2f}pt, LH={lh:.2f}...")
        update_css_parameters(margin, font, lh, gap)
        compile_pdf()
        pages = get_page_count()
        print(f"--> Result: {pages} pages")
        if pages == 9:
            print(f"\nSUCCESS: Exactly 9 pages achieved! (Margin={margin}in, Font={font}pt, LH={lh})")
            print(f"PDF Output: {PDF_PATH} ({os.path.getsize(PDF_PATH) / 1024:.2f} KB)")
            return

    # If not exactly 9 yet, report closest
    pages = get_page_count()
    print(f"\nFinal calibrated page count: {pages}")

if __name__ == "__main__":
    main()
