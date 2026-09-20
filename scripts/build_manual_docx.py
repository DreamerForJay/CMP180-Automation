"""Convert the CMP180 user manual HTML into a styled .docx using only the stdlib.

The manual is authored as the single source of truth in HTML; this script walks a
minimal DOM of that file and emits WordprocessingML so the Word edition keeps the
same headings, callouts, tables and code blocks.
"""

from __future__ import annotations

import html
import re
import sys
import zipfile
from html.parser import HTMLParser

VOID = {"br", "hr", "img", "meta", "link", "input"}

SANS_A = "Segoe UI"
SANS_E = "Microsoft JhengHei"
MONO_A = "Consolas"

# 色票與 HTML 版一致，讓 Word 與網頁／PDF 看起來是同一份文件。
NAVY = "10294A"
NAVY2 = "1D4674"
ACCENT = "0D8FA8"
INK = "12181F"
INK_SOFT = "4A5560"
BOX = {
    "tip": ("E6F6F9", "076477", "重點"),
    "warn": ("FFF5E2", "A1670A", "注意"),
    "danger": ("FDECEA", "B3261E", "警告"),
    "note": ("ECF1FD", "2B4F9E", "說明"),
    "ok": ("E8F6EE", "1F6B45", "完成"),
}


class Node:
    __slots__ = ("tag", "attrs", "kids", "text")

    def __init__(self, tag, attrs=None, text=""):
        self.tag = tag
        self.attrs = attrs or {}
        self.kids = []
        self.text = text

    def cls(self):
        return self.attrs.get("class", "").split()

    def find(self, tag, cls=None):
        for k in self.kids:
            if k.tag == tag and (cls is None or cls in k.cls()):
                return k
        return None


class Dom(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].kids.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].kids.append(Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].kids.append(Node("#text", text=data))


def esc(s):
    return html.escape(s, quote=False).replace("\r", "")


# --------------------------------------------------------------------------
# run / paragraph builders
# --------------------------------------------------------------------------
def run(text, *, b=False, mono=False, color=None, sz=None, shd=None):
    if not text:
        return ""
    rpr = [f"<w:rFonts w:ascii=\"{MONO_A if mono else SANS_A}\" w:hAnsi=\"{MONO_A if mono else SANS_A}\" w:eastAsia=\"{SANS_E}\" w:cs=\"{MONO_A if mono else SANS_A}\"/>"]
    if b:
        rpr.append("<w:b/><w:bCs/>")
    if color:
        rpr.append(f'<w:color w:val="{color}"/>')
    if sz:
        rpr.append(f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>')
    if shd:
        rpr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shd}"/>')
    return "<w:r><w:rPr>{}</w:rPr><w:t xml:space=\"preserve\">{}</w:t></w:r>".format("".join(rpr), esc(text))


def inline(node, *, b=False, base_color=None, sz=None):
    """Flatten inline children into runs, honouring strong/code/kbd/em."""
    out = []
    for k in node.kids:
        if k.tag == "#text":
            out.append(run(re.sub(r"\s+", " ", k.text), b=b, color=base_color, sz=sz))
        elif k.tag in ("strong", "b"):
            out.append(inline(k, b=True, base_color=NAVY, sz=sz))
        elif k.tag in ("code", "kbd"):
            out.append(run(text_of(k), mono=True, color="08596A", sz=(sz - 2) if sz else 19,
                           shd="EDF7F9"))
        elif k.tag in ("em", "i"):
            out.append(f"<w:r><w:rPr><w:i/></w:rPr><w:t xml:space=\"preserve\">{esc(text_of(k))}</w:t></w:r>")
        elif k.tag == "br":
            out.append("<w:r><w:br/></w:r>")
        elif k.tag == "span":
            out.append(run(text_of(k), b=True, color=base_color or INK, sz=sz))
        else:
            out.append(inline(k, b=b, base_color=base_color, sz=sz))
    return "".join(out)


def text_of(node):
    if node.tag == "#text":
        return node.text
    return "".join(text_of(k) for k in node.kids)


def para(runs, *, style=None, ind=0, space_before=0, space_after=120, shd=None,
         bar=None, border_bottom=None, page_break=False, align=None, keep=False):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if page_break:
        ppr.append("<w:pageBreakBefore/>")
    if keep:
        ppr.append("<w:keepNext/>")
    if shd:
        ppr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shd}"/>')
    bd = []
    if bar:
        bd.append(f'<w:left w:val="single" w:sz="24" w:space="8" w:color="{bar}"/>')
    if border_bottom:
        bd.append(f'<w:bottom w:val="single" w:sz="18" w:space="4" w:color="{border_bottom}"/>')
    if bd:
        ppr.append("<w:pBdr>{}</w:pBdr>".format("".join(bd)))
    if ind:
        ppr.append(f'<w:ind w:left="{ind}"/>')
    ppr.append(
        f'<w:spacing w:before="{space_before}" w:after="{space_after}"'
        ' w:line="290" w:lineRule="auto"/>'
    )
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    return "<w:p><w:pPr>{}</w:pPr>{}</w:p>".format("".join(ppr), runs)


def code_block(text):
    lines = [ln.rstrip() for ln in text.strip("\n").split("\n")]
    out = []
    for i, ln in enumerate(lines):
        before = 60 if i == 0 else 0
        after = 60 if i == len(lines) - 1 else 0
        ppr = ['<w:shd w:val="clear" w:color="auto" w:fill="F2F5F8"/>',
               '<w:ind w:left="170" w:right="170"/>',
               f'<w:spacing w:before="{before}" w:after="{after}"'
               ' w:line="240" w:lineRule="auto"/>']
        bd = [f'<w:left w:val="single" w:sz="18" w:space="6" w:color="{NAVY2}"/>']
        if i == 0:
            bd.append('<w:top w:val="single" w:sz="6" w:space="2" w:color="D6DEE7"/>')
        if i == len(lines) - 1:
            bd.append('<w:bottom w:val="single" w:sz="6" w:space="2" w:color="D6DEE7"/>')
        ppr.append("<w:pBdr>{}</w:pBdr>".format("".join(bd)))
        colour = "6E8299" if ln.lstrip().startswith("#") else "16324F"
        out.append("<w:p><w:pPr>{}</w:pPr>{}</w:p>".format("".join(ppr), run(ln or " ", mono=True, color=colour, sz=17)))
    return "".join(out)


def cell(runs_xml, *, w=0, fill=None, header=False):
    tcpr = [f'<w:tcW w:w="{w or 0}" w:type="{"dxa" if w else "auto"}"/>']
    if fill:
        tcpr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>')
    tcpr.append('<w:tcMar><w:top w:w="70" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/>'
                '<w:left w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tcMar>')
    tcpr.append("<w:vAlign w:val=\"top\"/>")
    body = runs_xml or para("")
    return "<w:tc><w:tcPr>{}</w:tcPr>{}</w:tc>".format("".join(tcpr), body)


def table(rows_xml, widths):
    grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in widths)
    tblpr = (
        '<w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        '<w:left w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="C9D3DE"/>'
        "</w:tblBorders>"
        '<w:tblLayout w:type="fixed"/></w:tblPr>'
    )
    return "<w:tbl>{}<w:tblGrid>{}</w:tblGrid>{}</w:tbl>{}".format(
        tblpr, grid, rows_xml, para("", space_after=140))


# --------------------------------------------------------------------------
# block conversion
# --------------------------------------------------------------------------
def conv_list(node, depth=0, ordered=False):
    out = []
    idx = 0
    for li in node.kids:
        if li.tag != "li":
            continue
        idx += 1
        marker = f"{idx}. " if ordered else ("• " if depth == 0 else "– ")
        head = run(marker, b=ordered, color=ACCENT)
        body = []
        nested = []
        for k in li.kids:
            if k.tag in ("ul", "ol"):
                nested.append(conv_list(k, depth + 1, k.tag == "ol"))
            else:
                body.append(inline(wrap_one(k)))
        out.append(para(head + "".join(body), ind=340 + depth * 300, space_after=70))
        out.extend(nested)
    return "".join(out)


def wrap_one(node):
    holder = Node("span")
    holder.kids = [node]
    return holder


def conv_steps(node):
    out = []
    for i, li in enumerate(node.kids, 1):
        if li.tag != "li":
            continue
        st = li.find("span", "st")
        title = text_of(st).strip() if st else ""
        rest = Node("div")
        rest.kids = [k for k in li.kids if k is not st]
        if title:
            out.append(para(run(f"STEP {i}  ", b=True, color=ACCENT, sz=19)
                            + run(title, b=True, color=NAVY, sz=23),
                            ind=200, space_before=110, space_after=40, keep=True))
        body = []
        for k in rest.kids:
            if k.tag == "pre":
                body.append(code_block(text_of(k)))
            elif k.tag in ("ul", "ol"):
                body.append(conv_list(k, 1, k.tag == "ol"))
            else:
                body.append(None)
        txt = inline(strip_blocks(rest))
        if txt.strip():
            out.append(para(txt, ind=200, space_after=80))
        out.extend([b for b in body if b])
    return "".join(out)


def strip_blocks(node):
    keep = Node("div")
    keep.kids = [k for k in node.kids if k.tag not in ("pre", "ul", "ol", "table", "div")]
    return keep


def conv_table(tbl):
    heads, body_rows = [], []
    for section in tbl.kids:
        if section.tag == "thead":
            for tr in section.kids:
                if tr.tag == "tr":
                    heads = [c for c in tr.kids if c.tag in ("th", "td")]
        elif section.tag == "tbody":
            for tr in section.kids:
                if tr.tag == "tr":
                    body_rows.append([c for c in tr.kids if c.tag in ("th", "td")])
    ncol = max([len(heads)] + [len(r) for r in body_rows] or [1])
    if ncol == 0:
        return ""
    total = 9070
    widths = [total // ncol] * ncol
    rows = []
    if heads:
        cells = "".join(
            cell(para(inline(h, b=True, base_color="FFFFFF", sz=19), space_after=0), w=widths[i],
                 fill=NAVY, header=True)
            for i, h in enumerate(heads))
        rows.append(f'<w:tr><w:trPr><w:tblHeader/></w:trPr>{cells}</w:tr>')
    for ri, r in enumerate(body_rows):
        fill = "F6F8FB" if ri % 2 else None
        cells = "".join(
            cell(para(inline(c, sz=19), space_after=0), w=widths[i], fill=fill)
            for i, c in enumerate(r))
        cells += "".join(cell(para(""), w=widths[i], fill=fill)
                         for i in range(len(r), ncol))
        rows.append(f"<w:tr>{cells}</w:tr>")
    return table("".join(rows), widths)


def conv_box(node):
    kind = next((c for c in node.cls() if c in BOX), "note")
    fill, colour, fallback = BOX[kind]
    out = []
    t = node.find("p", "t")
    label = text_of(t).strip() if t else fallback
    out.append(para(run(f"【{fallback}】 ", b=True, color=colour, sz=19)
                    + run(label, b=True, color=colour, sz=21),
                    shd=fill, bar=colour, space_before=140, space_after=0, keep=True))
    for k in node.kids:
        if k is t:
            continue
        if k.tag == "p":
            out.append(para(inline(k, sz=21), shd=fill, bar=colour, space_after=0))
        elif k.tag in ("ul", "ol"):
            for i, li in enumerate([x for x in k.kids if x.tag == "li"], 1):
                marker = f"{i}. " if k.tag == "ol" else "• "
                out.append(para(run(marker, color=colour, b=True) + inline(li, sz=21),
                                shd=fill, bar=colour, ind=280, space_after=0))
        elif k.tag == "pre":
            out.append(code_block(text_of(k)))
    out.append(para("", shd=fill, bar=colour, space_after=0))
    out.append(para("", space_after=100))
    return "".join(out)


def conv_faq(node):
    out = []
    summary = node.find("summary")
    q = text_of(summary).strip() if summary else ""
    out.append(para(run("Q  ", b=True, color="FFFFFF", sz=20, shd=ACCENT)
                    + run("  " + q, b=True, color=NAVY, sz=22),
                    shd="F1F4F8", space_before=150, space_after=0, keep=True))
    body = node.find("div", "body")
    if body:
        out.extend(conv_blocks(body.kids, indent=170))
    out.append(para("", space_after=90))
    return "".join(out)


def conv_kv(node):
    pairs = [k for k in node.kids if k.tag == "div"]
    rows = []
    for i in range(0, len(pairs) - 1, 2):
        fill = "F6F8FB" if i % 4 == 0 else None
        rows.append("<w:tr>{}{}</w:tr>".format(
            cell(para(inline(pairs[i], b=True, base_color=NAVY, sz=19), space_after=0),
                 w=2400, fill="EEF2F6"),
            cell(para(inline(pairs[i + 1], sz=19), space_after=0), w=6670, fill=fill)))
    return table("".join(rows), [2400, 6670])


def conv_cards(node):
    out = []
    for c in node.kids:
        if c.tag != "div" or "card" not in c.cls():
            continue
        h = c.find("div", "h")
        out.append(para(run("▍ ", color=ACCENT, b=True)
                        + run(text_of(h).strip() if h else "", b=True, color=NAVY, sz=21),
                        space_before=90, space_after=20, keep=True))
        for k in c.kids:
            if k is h:
                continue
            if k.tag == "p":
                out.append(para(inline(k, sz=20, base_color=INK_SOFT), ind=220, space_after=40))
    out.append(para("", space_after=90))
    return "".join(out)


def conv_blocks(nodes, indent=0):
    out = []
    for n in nodes:
        if n.tag == "#text":
            continue
        cls = n.cls()
        if n.tag == "h1" and "sec" in cls:
            num = n.find("span", "num")
            label = text_of(num).strip() if num else ""
            rest = Node("h1")
            rest.kids = [k for k in n.kids if k is not num]
            title = re.sub(r"\s+", " ", text_of(rest)).strip()
            out.append(para(run(label + "　", b=True, color=ACCENT, sz=24)
                            + run(title, b=True, color=NAVY, sz=40),
                            page_break=True, space_before=0, space_after=60,
                            border_bottom=ACCENT, keep=True))
        elif n.tag == "h2":
            out.append(para(inline(n, b=True, base_color=NAVY2, sz=29),
                            bar=ACCENT, ind=140, space_before=320, space_after=80, keep=True))
        elif n.tag == "h3":
            out.append(para(inline(n, b=True, base_color=INK, sz=24),
                            space_before=220, space_after=60, ind=indent, keep=True))
        elif n.tag == "h4":
            out.append(para(inline(n, b=True, base_color=INK_SOFT, sz=22),
                            space_before=160, space_after=40, ind=indent, keep=True))
        elif n.tag == "p":
            sz = 24 if "lead" in cls else 21
            colour = INK_SOFT if "lead" in cls else None
            out.append(para(inline(n, sz=sz, base_color=colour), ind=indent, space_after=120))
        elif n.tag == "pre":
            out.append(code_block(text_of(n)))
        elif n.tag in ("ul", "ol"):
            out.append(conv_list(n, 0, n.tag == "ol") if "steps" not in cls else conv_steps(n))
        elif n.tag == "table":
            out.append(conv_table(n))
        elif n.tag == "details":
            out.append(conv_faq(n))
        elif n.tag == "div":
            if "box" in cls:
                out.append(conv_box(n))
            elif "kv" in cls:
                out.append(conv_kv(n))
            elif "cards" in cls:
                out.append(conv_cards(n))
            elif "tablewrap" in cls:
                out.append(conv_blocks(n.kids, indent))
            elif "footer" in cls:
                out.append(para("", space_after=200))
                out.append(para(inline(n, sz=18, base_color=INK_SOFT), align="center"))
            else:
                out.append(conv_blocks(n.kids, indent))
        elif n.tag == "hr":
            out.append(para("", border_bottom="D6DEE7", space_after=180))
    return "".join(out)


# --------------------------------------------------------------------------
# document assembly
# --------------------------------------------------------------------------
def cover_xml(dom):
    cover = None
    for n in walk(dom):
        if n.tag == "header" and "cover" in n.cls():
            cover = n
            break
    out = [para("", space_after=1400)]
    if cover is None:
        return "".join(out)
    kick = cover.find("div", "kicker")
    h1 = cover.find("h1")
    sub = cover.find("p", "sub")
    meta = cover.find("div", "meta")
    out.append(para(run(text_of(kick).strip(), b=True, color=ACCENT, sz=20),
                    align="center", space_after=200))
    title = [re.sub(r"\s+", " ", t).strip() for t in
             re.split(r"\n", text_of(h1).replace(" ", " "))]
    for line in [x for x in " ".join(title).split("  ") if x.strip()]:
        pass
    out.append(para(run("CMP180 WLAN TX EVM", b=True, color=NAVY, sz=60),
                    align="center", space_after=60))
    out.append(para(run("自動化量測系統", b=True, color=NAVY, sz=60),
                    align="center", space_after=160))
    out.append(para(run("完　整　使　用　手　冊", b=True, color=ACCENT, sz=32),
                    align="center", space_after=420))
    if sub:
        out.append(para(inline(sub, sz=22, base_color=INK_SOFT), align="center", space_after=600))
    if meta:
        rows = []
        items = [text_of(s).strip() for s in meta.kids if s.tag == "span"]
        for it in items:
            parts = it.split(" ", 1)
            rows.append("<w:tr>{}{}</w:tr>".format(
                cell(para(run(parts[0], b=True, color=NAVY, sz=19), space_after=0),
                     w=2400, fill="EEF2F6"),
                cell(para(run(parts[1] if len(parts) > 1 else "", sz=19), space_after=0),
                     w=4400)))
        out.append(table("".join(rows), [2400, 4400]))
    out.append(para("", page_break=True, space_after=0))
    return "".join(out)


def walk(node):
    yield node
    for k in node.kids:
        yield from walk(k)


DOC_TMPL = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body>{body}
<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>
<w:pgMar w:top="1134" w:right="1021" w:bottom="1276" w:left="1021" w:header="708" w:footer="708" w:gutter="0"/>
</w:sectPr></w:body></w:document>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Segoe UI" w:hAnsi="Segoe UI" w:eastAsia="Microsoft JhengHei" w:cs="Segoe UI"/>
<w:sz w:val="21"/><w:szCs w:val="21"/><w:color w:val="12181F"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="290" w:lineRule="auto"/></w:pPr></w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
</w:styles>"""

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""

CORE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>CMP180 WLAN TX EVM 自動化量測系統 — 完整使用手冊</dc:title>
<dc:creator>CMP180-Automation</dc:creator>
<cp:lastModifiedBy>CMP180-Automation</cp:lastModifiedBy>
</cp:coreProperties>"""

APP = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>CMP180-Automation docs pipeline</Application>
</Properties>"""


def main(src, dst):
    raw = open(src, encoding="utf-8").read()
    raw = re.sub(r"<style.*?</style>", "", raw, flags=re.S)
    raw = re.sub(r"<nav.*?</nav>", "", raw, flags=re.S)
    dom = Dom()
    dom.feed(raw)
    wrap = next((n for n in walk(dom.root) if n.tag == "div" and "wrap" in n.cls()), None)
    if wrap is None:
        raise SystemExit("no .wrap container found")
    body = cover_xml(dom.root) + conv_blocks(wrap.kids)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", DOC_TMPL.format(body=body))
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("docProps/app.xml", APP)
    print("wrote", dst)


DEFAULT_SRC = "docs/manual/cmp180-user-manual.html"
DEFAULT_DST = "docs/manual/cmp180-user-manual.docx"

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SRC
    dst = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DST
    main(src, dst)
