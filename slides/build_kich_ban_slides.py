# -*- coding: utf-8 -*-
"""Kịch bản 1 người, mỗi trang A4 gồm 2 slide kèm lời nói ngay bên dưới từng slide.
Nguồn lời nói: kich-ban-1-nguoi.md; hình slide: final-defense.pdf (chỉ dùng trang 1-31, bài chính).
Đầu ra: Kich-ban-kem-slide-1-nguoi.docx và .pdf
Chạy: python3 build_kich_ban_slides.py   (trong thư mục slides; cần pdftoppm, soffice)
"""
import re
import subprocess
import tempfile
import pathlib
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / 'kich-ban-1-nguoi.md'
PDF = HERE / 'final-defense.pdf'
OUT = HERE / 'Kich-ban-kem-slide-1-nguoi.docx'
FONT = 'Arial'

# bảng màu theo từng phần: (màu đậm, màu nền nhạt)
PALETTE = {
    'mo':   ('042864', 'E8EEF8'),
    'p1':   ('005A8C', 'E6F2F8'),
    'p2':   ('0E7C7B', 'E4F4F3'),
    'p3':   ('CE1628', 'FCEBEC'),
    'p4':   ('8A5A00', 'FBF0DC'),
    'p5':   ('1F6F3D', 'E6F5EA'),
    'ket':  ('5B2A86', 'F0EAF6'),
}
GREY = '5A6472'

# ---------------- đọc kịch bản ----------------
lines = SRC.read_text(encoding='utf-8').split('\n')
slide_re = re.compile(r'^\*\*\[(\d+)(?:–(\d+))?\]\s*(.*?)\s*\((\d+:\d+)\)\*\*$')
blocks = []       # mỗi phần tử: dict(a, b, title, time, part, paras[(text, italic)])
part = 'mo'
cur = None
qa, numbers, tips = [], [], []
mode = 'slides'
i = 0
while i < len(lines):
    ln = lines[i].rstrip()
    s = ln.strip()
    i += 1
    if s.startswith('## '):
        t = s[3:]
        if t.startswith('Phần mở đầu'): part = 'mo'; mode = 'slides'
        elif t.startswith('Phần 1'): part = 'p1'
        elif t.startswith('Phần 2'): part = 'p2'
        elif t.startswith('Phần 3'): part = 'p3'
        elif t.startswith('Phần 4'): part = 'p4'
        elif t.startswith('Phần 5'): part = 'p5'
        elif t.startswith('Kết'): part = 'ket'
        elif t.startswith('Hỏi đáp'): mode = 'qa'
        elif t.startswith('Số cần nhớ'): mode = 'numbers'
        elif t.startswith('Mẹo'): mode = 'tips'
        cur = None
        continue
    if mode == 'slides':
        m = slide_re.match(s)
        if m:
            cur = dict(a=int(m.group(1)), b=int(m.group(2) or m.group(1)), title=m.group(3),
                       time=m.group(4), part=part, paras=[])
            blocks.append(cur)
            continue
        if cur is not None and s and s != '---':
            italic = s.startswith('*') and s.endswith('*') and not s.startswith('**')
            cur['paras'].append((s.strip('*') if italic else s, italic))
    elif mode == 'qa':
        if re.match(r'^\d+\.\s+\*\*', s):
            q = re.sub(r'^\d+\.\s+\*\*(.*)\*\*$', r'\1', s)
            ans = lines[i].strip() if i < len(lines) and lines[i].startswith('   ') else ''
            if ans:
                i += 1
            qa.append((q, ans))
    elif mode == 'numbers':
        if s.startswith('- '):
            numbers.append(s[2:])
    elif mode == 'tips':
        if s.startswith('- '):
            tips.append(s[2:])


def clean(t):
    t = t.replace('`', '')
    t = re.sub(r'\*\*(.+?)\*\*', r'\1', t)
    return t


def secs(t):
    a, b = t.split(':')
    return int(a) * 60 + int(b)


total = sum(secs(b['time']) for b in blocks)

# ---------------- hình slide ----------------
tmp = pathlib.Path(tempfile.mkdtemp())
subprocess.run(['pdftoppm', '-r', '170', '-f', '1', '-l', '31', '-png', str(PDF), str(tmp / 's')], check=True)
imgs = {int(re.search(r's-(\d+)\.png', p.name).group(1)): p for p in tmp.glob('s-*.png')}

# ---------------- tài liệu ----------------
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.5)
sec.top_margin, sec.bottom_margin = Cm(1.4), Cm(1.2)
sec.header_distance = Cm(0.6)
sec.footer_distance = Cm(0.5)
W = 18.0

normal = doc.styles['Normal']
normal.font.name = FONT
normal.font.size = Pt(10.5)
rpr = normal.element.get_or_add_rPr()
rf = rpr.find(qn('w:rFonts'))
if rf is None:
    rf = OxmlElement('w:rFonts'); rpr.append(rf)
for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
    rf.set(qn(a), FONT)
normal.paragraph_format.space_before = Pt(0)
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.line_spacing = 1.12


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcolor)
    tcPr.append(shd)


def cell_margins(cell, top=60, bottom=60, left=110, right=110):
    tcPr = cell._tc.get_or_add_tcPr()
    m = OxmlElement('w:tcMar')
    for k, v in (('top', top), ('left', left), ('bottom', bottom), ('right', right)):
        e = OxmlElement('w:' + k); e.set(qn('w:w'), str(v)); e.set(qn('w:type'), 'dxa'); m.append(e)
    tcPr.append(m)


def borders(table, color=None, sz=0, sides=('top', 'left', 'bottom', 'right', 'insideH', 'insideV')):
    tblPr = table._tbl.tblPr
    b = OxmlElement('w:tblBorders')
    for s in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement('w:' + s)
        if color and s in sides:
            e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), str(sz)); e.set(qn('w:color'), color)
        else:
            e.set(qn('w:val'), 'nil')
        e.set(qn('w:space'), '0')
        b.append(e)
    tblPr.append(b)


def fixed_layout(table, widths):
    tblPr = table._tbl.tblPr
    lay = OxmlElement('w:tblLayout'); lay.set(qn('w:type'), 'fixed'); tblPr.append(lay)
    table.autofit = False
    for ci, w in enumerate(widths):
        table.columns[ci].width = Cm(w)
        for r in table.rows:
            r.cells[ci].width = Cm(w)


def no_split(row):
    row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))


def run(p, text, size=None, bold=False, italic=False, color=None):
    r = p.add_run(text)
    r.font.name = FONT
    if size:
        r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color:
        r.font.color.rgb = RGBColor.from_string(color)
    return r


def spacer(pt=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(pt)
    r = p.add_run(''); r.font.size = Pt(2)
    return p


def add_field(par, instr):
    r = par.add_run()
    for kind, text in (('begin', None), ('instr', instr), ('separate', None), ('text', '1'), ('end', None)):
        if kind == 'instr':
            e = OxmlElement('w:instrText'); e.set(qn('xml:space'), 'preserve'); e.text = text
        elif kind == 'text':
            e = OxmlElement('w:t'); e.text = text
        else:
            e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), kind)
        r._r.append(e)
    r.font.size = Pt(9)
    r.font.color.rgb = RGBColor.from_string(GREY)


# đầu trang và chân trang
hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
run(hp, 'KỊCH BẢN THUYẾT TRÌNH  ·  Tích hợp dữ liệu khí tượng đa nguồn Đông Nam Á  ·  Nhóm 16, IT5427',
    size=8.5, color=GREY)
fp = sec.footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(fp, 'Trang ', size=9, color=GREY)
add_field(fp, 'PAGE')


def title_band():
    t = doc.add_table(rows=1, cols=2)
    fixed_layout(t, [13.2, 4.8]); borders(t)
    c0, c1 = t.rows[0].cells
    shade(c0, PALETTE['mo'][0]); shade(c1, PALETTE['p3'][0])
    for c in (c0, c1):
        cell_margins(c, 110, 110, 160, 160); c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c0.paragraphs[0]
    run(p, 'KỊCH BẢN THUYẾT TRÌNH', size=17, bold=True, color='FFFFFF')
    p2 = c0.add_paragraph()
    run(p2, 'Một người đọc để chạy thử  ·  mỗi slide kèm lời nói bên dưới', size=9.5, color='C9D6EE')
    q = c1.paragraphs[0]; q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(q, '%d:%02d' % (total // 60, total % 60), size=20, bold=True, color='FFFFFF')
    q2 = c1.add_paragraph(); q2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(q2, 'phút:giây (bài chính)', size=8.5, color='FFFFFF')
    spacer(5)


def slide_block(b):
    dark, light = PALETTE[b['part']]
    label = 'SLIDE %d' % b['a'] if b['a'] == b['b'] else 'SLIDE %d–%d' % (b['a'], b['b'])
    # thanh tiêu đề ba ô: nhãn | tiêu đề | thời gian
    h = doc.add_table(rows=1, cols=3)
    fixed_layout(h, [3.4, 11.8, 2.8]); borders(h)
    c0, c1, c2 = h.rows[0].cells
    for c, col in ((c0, dark), (c1, light), (c2, dark)):
        shade(c, col); cell_margins(c, 55, 55, 110, 110); c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = c0.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, label, size=11, bold=True, color='FFFFFF')
    p = c1.paragraphs[0]
    run(p, b['title'], size=12, bold=True, color=dark)
    p = c2.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, '⏱ ' + b['time'], size=11, bold=True, color='FFFFFF')
    no_split(h.rows[0])
    # hình slide, căn giữa, viền theo màu phần
    holder = doc.add_table(rows=1, cols=1)
    fixed_layout(holder, [W]); borders(holder, light, 8, sides=('left', 'right'))
    hc = holder.rows[0].cells[0]
    shade(hc, 'FFFFFF'); cell_margins(hc, 80, 80, 80, 80)
    hp_ = hc.paragraphs[0]; hp_.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if b['a'] == b['b']:
        hp_.add_run().add_picture(str(imgs[b['a']]), width=Cm(12.6))
    else:  # nhiều slide chung một lời nói: xếp ngang
        for k in range(b['a'], b['b'] + 1):
            hp_.add_run().add_picture(str(imgs[k]), width=Cm(8.6))
            hp_.add_run('  ')
    no_split(holder.rows[0])
    # lời nói
    t = doc.add_table(rows=1, cols=1)
    fixed_layout(t, [W]); borders(t, dark, 6, sides=('left', 'right', 'bottom'))
    c = t.rows[0].cells[0]
    shade(c, light); cell_margins(c, 80, 90, 170, 170)
    first = True
    for text, italic in b['paras']:
        p = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        p.paragraph_format.space_after = Pt(3)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if italic:
            run(p, '▸ Ghi chú: ' + clean(text), size=10, italic=True, color=dark)
        else:
            run(p, clean(text), size=11, color='1B1F27')
    no_split(t.rows[0])


def page_break():
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)
    p.paragraph_format.line_spacing = Pt(2)


# ---------------- các trang slide: 2 slide / trang ----------------
title_band()
for n, b in enumerate(blocks):
    if n > 0 and n % 2 == 0:
        page_break()
    elif n % 2 == 1:
        spacer(9)
    slide_block(b)

# ---------------- hỏi đáp ----------------
page_break()
t = doc.add_table(rows=1, cols=1)
fixed_layout(t, [W]); borders(t)
c = t.rows[0].cells[0]; shade(c, PALETTE['ket'][0]); cell_margins(c, 90, 90, 160, 160)
run(c.paragraphs[0], 'HỎI ĐÁP: CÂU HỎI DỄ GẶP VÀ GỢI Ý TRẢ LỜI', size=14, bold=True, color='FFFFFF')
spacer(6)
for k, (q, a) in enumerate(qa, 1):
    dark, light = PALETTE[['p1', 'p2', 'p3', 'p4', 'p5', 'ket', 'mo'][k % 7]]
    tb = doc.add_table(rows=2, cols=2)
    fixed_layout(tb, [1.6, 16.4]); borders(tb)
    no_split(tb.rows[0]); no_split(tb.rows[1])
    q0, q1 = tb.rows[0].cells
    a0, a1 = tb.rows[1].cells
    shade(q0, dark); shade(q1, light); shade(a0, dark); shade(a1, 'FFFFFF')
    for cc in (q0, q1, a0, a1):
        cell_margins(cc, 55, 55, 110, 110)
    m = q0.merge(a0)   # ô số thứ tự chiếm hai dòng
    shade(m, dark); m.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    pn = m.paragraphs[0]; pn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(pn, str(k), size=18, bold=True, color='FFFFFF')
    run(q1.paragraphs[0], clean(q), size=10.5, bold=True, color=dark)
    run(a1.paragraphs[0], clean(a), size=10.5, color='1B1F27')
    spacer(5)

# ---------------- số cần nhớ và mẹo ----------------
def box(title, items, key):
    dark, light = PALETTE[key]
    spacer(4)
    th = doc.add_table(rows=1, cols=1)
    fixed_layout(th, [W]); borders(th)
    c = th.rows[0].cells[0]; shade(c, dark); cell_margins(c, 70, 70, 160, 160)
    run(c.paragraphs[0], title, size=12, bold=True, color='FFFFFF')
    tb = doc.add_table(rows=1, cols=1)
    fixed_layout(tb, [W]); borders(tb, dark, 6, sides=('left', 'right', 'bottom'))
    c = tb.rows[0].cells[0]; shade(c, light); cell_margins(c, 80, 90, 170, 170)
    first = True
    for it in items:
        p = c.paragraphs[0] if first else c.add_paragraph()
        first = False
        p.paragraph_format.left_indent = Cm(0.45)
        p.paragraph_format.first_line_indent = Cm(-0.45)
        p.paragraph_format.space_after = Pt(3)
        run(p, '●  ', size=8, color=dark)
        run(p, clean(it), size=10, color='1B1F27')
    no_split(tb.rows[0])


page_break()
box('SỐ CẦN NHỚ', numbers, 'p1')
spacer(8)
box('MẸO KHI NÓI', tips, 'p3')

doc.save(str(OUT))
print('đã lưu', OUT, '| khối slide', len(blocks), '| hỏi đáp', len(qa), '| số', len(numbers), '| mẹo', len(tips))
subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(HERE), str(OUT)],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('đã xuất', OUT.with_suffix('.pdf'))
