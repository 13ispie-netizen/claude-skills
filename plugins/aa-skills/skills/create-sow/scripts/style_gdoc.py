#!/usr/bin/env python3
"""Build a Docs API batchUpdate that applies A+A branding to a scope proposal.

Usage: python3 style_gdoc.py <documents.get JSON> <out batch JSON>

Run on a FRESH read taken right after the HTML import, then send the output
in one documents.batchUpdate call. The batch carries the read's revisionId,
so it is rejected (not misapplied) if the doc changed in between.
"""
import json
import re
import sys

DARK, SAL, SHADE = "36354d", "f5a17d", "F2F2F2"


def col(h):
    return {"color": {"rgbColor": {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}}}


def ts(s, e, font, wt, size, c, bold):
    # Docs only keeps weights >= 700 when bold is true (Black = 900, ExtraBold = 800).
    return {"updateTextStyle": {"range": {"startIndex": s, "endIndex": e},
            "textStyle": {"weightedFontFamily": {"fontFamily": font, "weight": wt}, "fontSize": {"magnitude": size, "unit": "PT"},
                          "foregroundColor": col(c), "bold": bold},
            "fields": "weightedFontFamily,fontSize,foregroundColor,bold"}}


def ps(s, e, style, fields):
    return {"updateParagraphStyle": {"range": {"startIndex": s, "endIndex": e}, "paragraphStyle": style, "fields": fields}}


def pt(n):
    return {"magnitude": n, "unit": "PT"}


def runs(p):
    return [r for r in p["elements"] if "textRun" in r]


def style_body(d, reqs):
    for el in d["body"]["content"]:
        p = el.get("paragraph")
        if not p:
            continue
        s, e = el["startIndex"], el["endIndex"]
        ns = p["paragraphStyle"].get("namedStyleType")
        txt = "".join(x.get("textRun", {}).get("content", "") for x in p["elements"])
        if not txt.strip():
            continue
        if txt.startswith("ARCHITECTURE + ADVOCACY") and s < 10:
            reqs.append(ts(s, e, "Public Sans", 200, 13, SAL, False))
        elif "| PREPARED" in txt and s < 200:
            reqs.append(ts(s, e, "Public Sans", 300, 11, SAL, False))
            reqs.append(ps(s, e, {"borderBottom": {"color": col(DARK), "width": pt(0.75), "padding": pt(6), "dashStyle": "SOLID"},
                                  "spaceBelow": pt(12)}, "borderBottom,spaceBelow"))
        elif ns == "HEADING_1":
            for r in runs(p):
                reqs.append(ts(r["startIndex"], r["endIndex"], "Public Sans", 900, 19, DARK, True))
        elif ns == "HEADING_2":
            for r in runs(p):
                reqs.append(ts(r["startIndex"], r["endIndex"], "Public Sans", 200, 13, SAL, False))
        elif ns == "HEADING_3":
            for r in runs(p):
                reqs.append(ts(r["startIndex"], r["endIndex"], "Public Sans", 800, 12, DARK, True))
        else:
            for i, r in enumerate(runs(p)):
                b = bool(r["textRun"]["textStyle"].get("bold"))
                if b and i == 0 and re.match(r"\d+\.\d ", txt):  # "1.0 Task Name" label
                    reqs.append(ts(r["startIndex"], r["endIndex"], "Public Sans", 800, 11, DARK, True))
                else:
                    reqs.append(ts(r["startIndex"], r["endIndex"], "Nunito", 700 if b else 400, 11, DARK, b))
            if "bullet" in p:
                reqs.append(ps(s, e, {"spaceBelow": pt(3)}, "spaceBelow"))
            else:
                reqs.append(ps(s, e, {"spaceBelow": pt(8), "spaceAbove": pt(6), "lineSpacing": 115}, "spaceBelow,spaceAbove,lineSpacing"))
        if ns and ns.startswith("HEADING"):
            reqs.append(ps(s, e, {"keepWithNext": True}, "keepWithNext"))


def style_tables(d, reqs):
    border = {"color": col(DARK), "width": pt(0.5), "dashStyle": "SOLID"}
    for el in d["body"]["content"]:
        t = el.get("table")
        if not t:
            continue
        start = el["startIndex"]
        ncols = t["columns"]
        reqs.append({"updateTableCellStyle": {"tableRange": {"tableCellLocation": {"tableStartLocation": {"index": start}, "rowIndex": 0, "columnIndex": 0},
                                                             "rowSpan": 1, "columnSpan": ncols},
                                              "tableCellStyle": {"backgroundColor": col(SHADE)}, "fields": "backgroundColor"}})
        reqs.append({"updateTableCellStyle": {"tableStartLocation": {"index": start},
                                              "tableCellStyle": {"paddingTop": pt(4), "paddingBottom": pt(4), "paddingLeft": pt(5), "paddingRight": pt(5),
                                                                 "borderTop": border, "borderBottom": border, "borderLeft": border, "borderRight": border},
                                              "fields": "paddingTop,paddingBottom,paddingLeft,paddingRight,borderTop,borderBottom,borderLeft,borderRight"}})
        for row in t["tableRows"]:
            for cell in row["tableCells"]:
                for ce in cell["content"]:
                    p = ce.get("paragraph")
                    if not p:
                        continue
                    for r in runs(p):
                        b = bool(r["textRun"]["textStyle"].get("bold"))
                        reqs.append(ts(r["startIndex"], r["endIndex"], "Nunito", 700 if b else 400, 10, DARK, b))
                    if "bullet" in p:
                        reqs.append(ps(ce["startIndex"], ce["endIndex"], {"indentStart": pt(12), "indentFirstLine": pt(0), "spaceBelow": pt(2)},
                                       "indentStart,indentFirstLine,spaceBelow"))


def main():
    d = json.load(open(sys.argv[1]))
    reqs = []
    style_body(d, reqs)
    style_tables(d, reqs)
    json.dump({"requests": reqs, "writeControl": {"requiredRevisionId": d["revisionId"]}}, open(sys.argv[2], "w"))
    print(f"{len(reqs)} requests -> {sys.argv[2]}")


if __name__ == "__main__":
    main()
