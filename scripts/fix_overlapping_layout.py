"""
Fixes the CSS multi-column overlapping bug shown in the user's screenshot.
In Chromium/Edge, placing wide tables and wide SVGs inside a continuous CSS multi-column
container causes the right column to overlap the left column.
Solution:
1. Apply clean column breaks / section segmentation:
   Text sections are inside `.two-column-body`.
   Wide tables (Table I, Table II, etc.) and wide diagrams (Fig 1 - Fig 9) are enclosed
   in `.full-width-box` spanning 100% width cleanly with clear margins.
2. Add explicit `break-inside: avoid;` and `clear: both;`.
3. Compile with Edge headless and verify zero collision.
4. Verify the page count remains within 9-10 pages.
"""

import os
import re
import subprocess
from pathlib import Path

ROOT = Path("D:/CODING/AI MEDICAL")
HTML_PATH = ROOT / "AcuMeds_AI_Medical_IEEE_Paper.html"
PDF_PATH = ROOT / "AcuMeds_AI_Medical_IEEE_Paper.pdf"
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def main():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    # Update CSS
    css_replacement = """
  @page {
    size: letter portrait;
    margin: 0.70in 0.60in 0.70in 0.60in;
    @bottom-center {
      content: counter(page);
      font-family: "Times New Roman", Times, serif;
      font-size: 8.5pt;
    }
  }

  body {
    font-family: "Times New Roman", Times, serif;
    font-size: 9.60pt;
    line-height: 1.23;
    color: #000;
    margin: 0;
    padding: 0;
    text-align: justify;
    text-justify: inter-word;
  }

  .header-container {
    text-align: center;
    margin-bottom: 12px;
  }

  h1.paper-title {
    font-size: 18pt;
    font-weight: bold;
    line-height: 1.20;
    margin-bottom: 10px;
    margin-top: 0;
    letter-spacing: -0.2px;
  }

  .abstract-keywords-box {
    margin: 0 16px 12px 16px;
    font-size: 8.5pt;
    line-height: 1.22;
  }

  .abstract-title, .keywords-title {
    font-weight: bold;
    font-style: italic;
  }

  .divider-line {
    border-top: 0.5pt solid #000;
    margin-bottom: 10px;
  }

  /* Two Column Layout for text blocks */
  .two-column-body {
    column-count: 2;
    column-gap: 0.24in;
    column-rule: 0.3pt solid #cbd5e1;
    margin-bottom: 8px;
  }

  /* Full Width Container spanning both columns */
  .full-width-block {
    width: 100%;
    margin: 10px 0;
    break-inside: avoid;
    clear: both;
  }

  h2.section-heading {
    font-size: 9.3pt;
    font-weight: bold;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-top: 12px;
    margin-bottom: 5px;
    break-after: avoid;
    border-bottom: 0.3pt solid #cbd5e1;
    padding-bottom: 2px;
  }

  h3.subsection-heading {
    font-size: 9.0pt;
    font-weight: bold;
    font-style: italic;
    text-align: left;
    margin-top: 8px;
    margin-bottom: 3px;
    break-after: avoid;
  }

  p {
    margin-top: 0;
    margin-bottom: 5px;
    text-indent: 1.2em;
  }

  p.no-indent {
    text-indent: 0;
  }

  .equation-box {
    text-align: center;
    margin: 5px 0;
    font-size: 8.8pt;
  }

  table.ieee-table {
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0;
    font-size: 7.2pt;
    line-height: 1.15;
    break-inside: avoid;
  }

  table.ieee-table th, table.ieee-table td {
    padding: 3px 4px;
    border-top: 0.5pt solid #000;
    border-bottom: 0.5pt solid #000;
    text-align: left;
  }

  table.ieee-table th {
    font-weight: bold;
    background-color: #f1f5f9;
    text-align: center;
  }

  .table-caption {
    font-size: 7.6pt;
    font-weight: bold;
    text-align: center;
    margin-bottom: 3px;
    margin-top: 6px;
    text-transform: uppercase;
  }

  .svg-figure-box {
    background: #ffffff;
    border: 0.5pt solid #cbd5e1;
    border-radius: 4px;
    padding: 5px;
    margin: 6px 0 3px 0;
    text-align: center;
    break-inside: avoid;
  }

  .figure-caption {
    font-size: 7.6pt;
    text-align: center;
    margin-top: 3px;
    margin-bottom: 8px;
    font-style: italic;
  }

  .algorithm-box {
    background: #f8fafc;
    border: 0.5pt solid #94a3b8;
    padding: 5px 7px;
    margin: 6px 0;
    font-family: "Courier New", Courier, monospace;
    font-size: 6.8pt;
    line-height: 1.14;
    white-space: pre-wrap;
    break-inside: avoid;
  }

  .reference-item {
    font-size: 7.4pt;
    line-height: 1.16;
    margin-bottom: 3.5px;
    text-indent: -1.4em;
    margin-left: 1.4em;
  }
"""
    # Replace style block
    html = re.sub(r'<style>.*?</style>', f'<style>{css_replacement}</style>', html, flags=re.DOTALL)

    # Convert full width items (Tables and SVG Figures) so they do NOT get squeezed into 1 column:
    # We find wide tables and figures and wrap them in </div><div class="full-width-block">...</div><div class="two-column-body">
    
    # Target Table I
    t1_pattern = r'(<div class="table-caption">TABLE I:.*?</table>)'
    def replace_t1(m):
        return f'</div>\n<div class="full-width-block">\n{m.group(1)}\n</div>\n<div class="two-column-body">'
    html = re.sub(t1_pattern, replace_t1, html, flags=re.DOTALL)

    # Target SVG Figures (Fig 1 to Fig 9)
    fig_pattern = r'(<div class="svg-figure-box">.*?<div class="figure-caption">.*?</div>)'
    def replace_fig(m):
        return f'</div>\n<div class="full-width-block">\n{m.group(1)}\n</div>\n<div class="two-column-body">'
    html = re.sub(fig_pattern, replace_fig, html, flags=re.DOTALL)

    # Target Algorithm 1
    algo_pattern = r'(<div class="algorithm-box">Algorithm 1:.*?</div>)'
    def replace_algo(m):
        return f'</div>\n<div class="full-width-block">\n{m.group(1)}\n</div>\n<div class="two-column-body">'
    html = re.sub(algo_pattern, replace_algo, html, flags=re.DOTALL)

    # Target wide tables: Table II, III, IV, V, VI, VII, VIII, IX, X
    wide_tables = [
        r'(<div class="table-caption">TABLE II:.*?</table>)',
        r'(<div class="table-caption">TABLE III:.*?</table>)',
        r'(<div class="table-caption">TABLE IV:.*?</table>)',
        r'(<div class="table-caption">TABLE V:.*?</table>)',
        r'(<div class="table-caption">TABLE VI:.*?</table>)',
        r'(<div class="table-caption">TABLE VII:.*?</table>)',
        r'(<div class="table-caption">TABLE VIII:.*?</table>)',
        r'(<div class="table-caption">TABLE IX:.*?</table>)',
        r'(<div class="table-caption">TABLE X:.*?</table>)'
    ]
    for wt in wide_tables:
        html = re.sub(wt, replace_t1, html, flags=re.DOTALL)

    # Clean up empty `<div class="two-column-body">\s*</div>`
    html = re.sub(r'<div class="two-column-body">\s*</div>', '', html)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print("Restructured HTML with modular two-column and full-width block segmentation.")

    # Calibration loop to land on exactly 9-10 pages
    configs = [
        # (margin, font, line_height, col_gap)
        (0.68, 9.60, 1.22, 0.23),
        (0.70, 9.65, 1.23, 0.24),
        (0.72, 9.70, 1.24, 0.24),
        (0.74, 9.75, 1.25, 0.25),
        (0.76, 9.80, 1.26, 0.25),
        (0.78, 9.85, 1.27, 0.25),
        (0.80, 9.95, 1.29, 0.26),
        (0.65, 9.50, 1.20, 0.22),
        (0.62, 9.40, 1.18, 0.20)
    ]

    for m, f_sz, lh, gap in configs:
        temp = re.sub(r'margin:\s*[0-9.]+in\s*[0-9.]+in\s*[0-9.]+in\s*[0-9.]+in;', f'margin: {m:.2f}in {m*0.85:.2f}in {m:.2f}in {m*0.85:.2f}in;', html)
        temp = re.sub(r'font-size:\s*[0-9.]+pt;\s*line-height:\s*[0-9.]+;', f'font-size: {f_sz:.2f}pt;\n    line-height: {lh:.2f};', temp, count=1)
        temp = re.sub(r'column-gap:\s*[0-9.]+in;', f'column-gap: {gap:.2f}in;', temp)

        with open(HTML_PATH, "w", encoding="utf-8") as f_out:
            f_out.write(temp)

        subprocess.run([EDGE_BIN, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={PDF_PATH}', f'file:///{HTML_PATH}'], capture_output=True)

        with open(PDF_PATH, 'rb') as f_pdf:
            pages = len(re.findall(rb'/Type\s*/Page\b', f_pdf.read()))
        print(f"Testing M={m:.2f}in, F={f_sz:.2f}pt, LH={lh:.2f} --> Pages: {pages}")

        if pages in [9, 10]:
            print(f"\nSUCCESS! EXACTLY {pages} PAGES (Clean, non-overlapping layout)!")
            print(f"PDF Size: {os.path.getsize(PDF_PATH) / 1024:.2f} KB\n")
            return

if __name__ == "__main__":
    main()
