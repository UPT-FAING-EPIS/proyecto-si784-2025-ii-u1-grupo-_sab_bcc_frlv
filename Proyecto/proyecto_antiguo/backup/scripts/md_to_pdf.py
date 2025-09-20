#!/usr/bin/env python3
"""Convert simple Markdown to PDF using reportlab.
This script supports headings (#, ##), paragraphs and fenced code blocks ```.
"""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4

p = Path(__file__).resolve().parents[1] / 'demos' / 'presentation_snippet.md'
out = p.with_suffix('.pdf')
text = p.read_text(encoding='utf-8')
lines = text.splitlines()

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Code', fontName='Courier', fontSize=9, leading=11))
styles.add(ParagraphStyle(name='Heading1', parent=styles['Heading1'], spaceAfter=6))
styles.add(ParagraphStyle(name='Heading2', parent=styles['Heading2'], spaceAfter=4))

story = []

in_code = False
code_lines = []
para_lines = []

def flush_para():
    global para_lines
    if para_lines:
        t = '\n'.join(para_lines).strip()
        if t:
            story.append(Paragraph(t.replace('&','&amp;').replace('<','&lt;'), styles['Normal']))
            story.append(Spacer(1,4*mm))
    para_lines = []

for ln in lines:
    if ln.strip().startswith('```'):
        if in_code:
            # end code
            story.append(Preformatted('\n'.join(code_lines), styles['Code']))
            story.append(Spacer(1,4*mm))
            code_lines = []
            in_code = False
        else:
            flush_para()
            in_code = True
        continue
    if in_code:
        code_lines.append(ln)
        continue
    if ln.startswith('# '):
        flush_para()
        story.append(Paragraph(ln[2:].strip(), styles['Heading1']))
        continue
    if ln.startswith('## '):
        flush_para()
        story.append(Paragraph(ln[3:].strip(), styles['Heading2']))
        continue
    if ln.strip() == '':
        flush_para()
        continue
    para_lines.append(ln)

flush_para()

# build pdf
pdf = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
pdf.build(story)
print('Wrote:', out)
