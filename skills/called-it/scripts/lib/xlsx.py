"""A minimal .xlsx writer with no dependencies: several sheets, a bold frozen header row, column widths,
inline strings, numbers and booleans. Enough for the run workbooks; not a general spreadsheet library.

The file is a zip of XML parts in the Office Open XML layout Excel, Numbers, Google Sheets and
LibreOffice all read. Strings are written as inline strings (no shared-string table), which keeps the
writer small and the output deterministic.
"""
from __future__ import annotations

import datetime as dt
import zipfile
from xml.sax.saxutils import escape

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
{sheet_overrides}
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="3">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>"""


def _col(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(ref: str, v, style: int = 0) -> str:
    if v is None or v == "":
        return ""
    if isinstance(v, bool):
        return f'<c r="{ref}" t="b" s="{style}"><v>{int(v)}</v></c>'
    if isinstance(v, (int, float)):
        return f'<c r="{ref}" s="{style}"><v>{v}</v></c>'
    text = escape(str(v))
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)  # control chars are invalid in XML
    return f'<c r="{ref}" t="inlineStr" s="{style}"><is><t xml:space="preserve">{text}</t></is></c>'


def _sheet_xml(headers: list[str], rows: list[list], widths: list[int] | None, wrap_cols: set[int]) -> str:
    cols = ""
    if widths:
        cols = "<cols>" + "".join(f'<col min="{i + 1}" max="{i + 1}" width="{w}" customWidth="1"/>' for i, w in enumerate(widths)) + "</cols>"
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
           '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>',
           cols, "<sheetData>"]
    out.append('<row r="1">' + "".join(_cell(f"{_col(i + 1)}1", h, 1) for i, h in enumerate(headers)) + "</row>")
    for r, row in enumerate(rows, start=2):
        cells = "".join(_cell(f"{_col(i + 1)}{r}", v, 2 if i in wrap_cols else 0) for i, v in enumerate(row))
        out.append(f'<row r="{r}">{cells}</row>')
    out.append("</sheetData>")
    out.append(f'<autoFilter ref="A1:{_col(len(headers))}{max(len(rows) + 1, 1)}"/>' if headers else "")
    out.append("</worksheet>")
    return "".join(out)


def write_xlsx(path, sheets: list[dict], title: str = "", creator: str = "called-it") -> None:
    """sheets: [{"name": str, "headers": [...], "rows": [[...], ...], "widths": [...], "wrap": [col indexes]}]"""
    names = []
    for s in sheets:
        n = s["name"][:31]
        for ch in '[]:*?/\\':
            n = n.replace(ch, " ")
        names.append(n)
    now = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # fixed, so the file is reproducible
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES.format(sheet_overrides="\n".join(
            f'<Override PartName="/xl/worksheets/sheet{i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            for i in range(len(sheets)))))
        z.writestr("_rels/.rels", ROOT_RELS)
        z.writestr("docProps/core.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                   'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                   f'<dc:title>{escape(title)}</dc:title><dc:creator>{escape(creator)}</dc:creator>'
                   f'<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created>'
                   f'<dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>')
        z.writestr("docProps/app.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                   '<Application>called-it</Application></Properties>')
        z.writestr("xl/workbook.xml",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   + "".join(f'<sheet name="{escape(n)}" sheetId="{i + 1}" r:id="rId{i + 1}"/>' for i, n in enumerate(names))
                   + "</sheets></workbook>")
        z.writestr("xl/_rels/workbook.xml.rels",
                   '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(f'<Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i + 1}.xml"/>' for i in range(len(sheets)))
                   + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                   + "</Relationships>")
        z.writestr("xl/styles.xml", STYLES)
        for i, s in enumerate(sheets):
            z.writestr(f"xl/worksheets/sheet{i + 1}.xml", _sheet_xml(s["headers"], s["rows"], s.get("widths"), set(s.get("wrap", []))))
