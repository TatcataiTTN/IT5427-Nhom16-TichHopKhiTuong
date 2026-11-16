# -*- coding: utf-8 -*-
"""Thư viện sinh sơ đồ draw.io theme sáng, bảng màu thống nhất cho mọi sơ đồ thuật toán.
Vai trò màu (đồng nhất xuyên suốt): xanh dương = dữ liệu/trạng thái, vàng = bước xử lý, xanh lá = kết quả/ổn định,
đỏ = cảnh báo/xấu nhất/không ổn định, tím = kết luận/đầu ra, cam = ghi chú. Thanh tiêu đề: xanh đậm nhạt #3d5a80."""
import html, itertools
PAL = {  # vai trò: (nền, viền, chữ, thanh tiêu đề thẻ). Nền rất nhạt, viền vừa, chữ tối cùng tông, thanh đậm vừa để chữ trắng đọc rõ
 'blue':   ('#E8F1FD', '#5B9BD5', '#17375E', '#3F78B8'),
 'yellow': ('#FFF4D6', '#E3B341', '#5A4200', '#A8740A'),
 'green':  ('#E3F4E7', '#5DB07B', '#1B4D2B', '#3E8E5C'),
 'red':    ('#FDE6E4', '#E0736F', '#6B1F1C', '#C0443F'),
 'purple': ('#EEE8F8', '#9A7DCF', '#3F2A6B', '#7557B0'),
 'orange': ('#E3F3F4', '#5BAAB2', '#17494F', '#3A8A92'),   # ghi chú: tông xanh ngọc để không lẫn với vàng (bước xử lý)
 'grey':   ('#F4F6F9', '#B8C2CC', '#2A3340', '#6B7785'),
 'white':  ('#FFFFFF', '#B8C2CC', '#222B36', '#6B7785')}
BAR = '#2B4C7E'
FS = 1.22   # hệ số phóng chữ toàn cục: chữ to hơn mà khung A4 không đổi
FONT = 'Helvetica'
W, H = 1600, 1000
A4L = (1169, 827)   # khổ A4 ngang ở 96 dpi
A4P = (827, 1169)   # khổ A4 dọc
def esc(t): return html.escape(t, quote=True).replace('\n', '&#10;')
class Page:
    def __init__(self, name, title, subtitle='', w=1200, h=800):
        self.name, self.cells, self.n, self.W, self.H = name, [], itertools.count(2), w, h
        self.maxy = 0; self.fixed = False
        self.bar(0, 0, w, 54, title, 22)
        if subtitle: self.text(24, 58, w-48, 32, subtitle, 15, color='#555555', align='left')
    def a4(self, landscape=True):
        self.W, self.H = A4L if landscape else A4P; self.fixed = True; return self
    def _id(self): return f'c{next(self.n)}'
    def add(self, value, style, x, y, w, h, vertex=True):
        self.maxy = max(self.maxy, y + h)
        i = self._id()
        self.cells.append(f'<mxCell id="{i}" value="{esc(value)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return i
    def box(self, x, y, w, h, text, role='yellow', size=16, bold=False, shape='rounded', align='center', arc=12):
        f, s, tc, _ = PAL[role]
        base = {'rounded': f'rounded=1;arcSize={arc};', 'rect': 'rounded=0;', 'term': 'rounded=1;arcSize=50;', 'diamond': 'rhombus;', 'ellipse': 'ellipse;'}[shape]
        st = (f'{base}whiteSpace=wrap;html=1;fillColor={f};strokeColor={s};strokeWidth=1.8;fontSize={round(size*FS)};fontFamily={FONT};fontColor={tc};'
              f'align={align};verticalAlign=middle;spacingLeft=8;spacingRight=8;' + ('fontStyle=1;' if bold else ''))
        return self.add(text, st, x, y, w, h)
    def bar(self, x, y, w, h, text, size=17, color=None):
        color = color or BAR
        st = f'rounded=0;whiteSpace=wrap;html=1;fillColor={color};strokeColor={color};fontColor=#ffffff;fontSize={round(size*FS)};fontStyle=1;fontFamily={FONT};align=left;spacingLeft=16;'
        return self.add(text, st, x, y, w, h)
    def text(self, x, y, w, h, text, size=15, color='#222222', align='center', bold=False, italic=False):
        fs = (1 if bold else 0) + (2 if italic else 0)
        st = f'text;html=1;whiteSpace=wrap;align={align};verticalAlign=middle;fontSize={round(size*FS)};fontFamily={FONT};fontColor={color};fontStyle={fs};strokeColor=none;fillColor=none;'
        return self.add(text, st, x, y, w, h)
    def cell(self, x, y, w, h, text, role='white', size=16, bold=False):
        return self.box(x, y, w, h, text, role, size, bold, 'rect')
    def arrow(self, a, b, label='', pts=None, color='#4B5563', dashed=False, exit=None, entry=None, size=14):
        i = self._id()
        st = (f'edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;html=1;endArrow=block;endFill=1;strokeColor={color};strokeWidth=2;fontSize={round(size*FS)};fontFamily={FONT};fontColor=#333333;'
              + ('dashed=1;' if dashed else '') + (f'exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;' if exit else '') + (f'entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;' if entry else ''))
        pp = ''.join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in (pts or []))
        arr = f'<Array as="points">{pp}</Array>' if pp else ''
        self.cells.append(f'<mxCell id="{i}" value="{esc(label)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry">{arr}</mxGeometry></mxCell>')
    def line(self, x1, y1, x2, y2, color='#9a9a9a', dashed=False):
        i = self._id()
        st = f'endArrow=none;html=1;strokeColor={color};strokeWidth=1.2;' + ('dashed=1;' if dashed else '')
        self.cells.append(f'<mxCell id="{i}" style="{st}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>')
    def array(self, x, y, vals, cell=46, hi=None, label=None, size=17, role='blue', lw=165):
        hi = hi or {}
        if label: self.text(x-lw-10, y, lw, cell, label, 15, align='right', color='#444444')
        for k, v in enumerate(vals):
            self.cell(x + k*cell, y, cell, cell, str(v), hi.get(k, role), size, bold=(k in hi))
        return x + len(vals)*cell
    def finish(self):
        rows = 1 if self.W >= 1000 else 2
        need = int(self.maxy + 14 + rows*26 + 12)
        if self.fixed:
            if need > self.H: print(f'  !! {self.name}: noi dung vuot kho A4 {need} > {self.H}')
        else: self.H = need
        self.legend()
        return self
    def legend(self):
        items = [('blue', 'dữ liệu, trạng thái'), ('yellow', 'bước xử lý'), ('green', 'kết quả, ổn định'), ('red', 'cảnh báo, xấu nhất'), ('purple', 'kết luận, đầu ra'), ('orange', 'ghi chú')]
        per = 3 if self.W < 1000 else 6; colw = (self.W - 48) / per
        rows = (len(items) + per - 1) // per
        y0 = self.H - 12 - rows*26
        for k, (role, lab) in enumerate(items):
            f, st, _, _ = PAL[role]; x = 24 + (k % per)*colw; y = y0 + (k // per)*26
            self.add('', f'rounded=1;fillColor={f};strokeColor={st};', x, y+6, 22, 14, True)
            self.text(x+28, y, colw-34, 26, lab, 13, '#555555', 'left')
    def xml(self):
        return (f'<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{self.W}" pageHeight="{self.H}" background="#ffffff" math="0" shadow="0">'
                '<root><mxCell id="0"/><mxCell id="1" parent="0"/>' + ''.join(self.cells) + '</root></mxGraphModel>')
def write(page, path):
    page.finish()
    open(path, 'w', encoding='utf-8').write(f'<mxfile host="app.diagrams.net"><diagram name="{esc(page.name)}" id="d1">{page.xml()}</diagram></mxfile>')
def cards(p, x, y, w, items, size=15):
    """Khối thông tin chuẩn: (tiêu đề, nội dung, vai trò màu). Ước lượng số dòng theo bề rộng."""
    cpl = max(20, int((w - 24) / (size * FS * 0.52)))
    for title, body, role in items:
        lines = sum(max(1, -(-len(l) // cpl)) for l in body.split('\n'))
        bh = 16 + int(lines * size * FS * 1.38)
        p.bar(x, y, w, 34, title, size+1, PAL[role][3])
        p.box(x, y+34, w, bh, body, role, size, False, 'rect', 'left')
        y += 34 + bh + 12
    return y
