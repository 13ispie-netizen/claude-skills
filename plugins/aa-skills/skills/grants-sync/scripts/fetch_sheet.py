#!/usr/bin/env python3
"""Pull the FUTURE LOOKING tab with cell hyperlinks and fill colors intact.

A values-only or CSV export drops hyperlinks and fills. That is how the original
import lost every grant/org link, so this reads through the Sheets API with an
explicit field mask instead.

Output: JSON list of rows, one per non-empty sheet row.
"""

import argparse
import json
import subprocess
import sys

SPREADSHEET_ID = "1UrHVT6g9lloJSiagXrrFl1WYy7ttySoccbqZ3Ps79vQ"
TAB = "FUTURE LOOKING"
N_COLS = 25  # A..Y

FIELDS = "sheets.data.rowData.values(formattedValue,hyperlink,effectiveFormat.backgroundColorStyle)"

# 10+ tinted cells in a 25-cell row means the row is highlighted.
# Fewer than that is stray formatting on individual cells.
HIGHLIGHT_MIN_CELLS = 10


def run_gws(params):
    try:
        out = subprocess.run(
            ["gws", "sheets", "spreadsheets", "get", "--params", json.dumps(params)],
            capture_output=True, text=True, check=True,
        ).stdout
    except FileNotFoundError:
        sys.exit(
            "ERROR: the `gws` CLI is not available.\n"
            "Cell hyperlinks and fill colors cannot be read without it, and syncing "
            "without them would recreate the original lost-links bug.\n"
            "Run this skill in Claude Code, or ask Erin to sync there."
        )
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: gws failed: {e.stderr.strip()}")
    # gws prints a keyring banner before the JSON
    start = out.find("{")
    if start < 0:
        sys.exit(f"ERROR: no JSON in gws output: {out[:200]}")
    return json.loads(out[start:])


def cell(values, i, key="formattedValue"):
    return values[i].get(key) if i < len(values) else None


def is_tinted(values, i):
    """True if the cell has a non-white background."""
    if i >= len(values):
        return False
    rgb = (
        values[i]
        .get("effectiveFormat", {})
        .get("backgroundColorStyle", {})
        .get("rgbColor", {})
    )
    if not rgb:
        return False
    r = round(rgb.get("red", 0), 3)
    g = round(rgb.get("green", 0), 3)
    b = round(rgb.get("blue", 0), 3)
    return (r, g, b) != (1.0, 1.0, 1.0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    props = run_gws({
        "spreadsheetId": SPREADSHEET_ID,
        "fields": "sheets.properties(sheetId,title,gridProperties.rowCount)",
    })
    n_rows = None
    for s in props.get("sheets", []):
        if s["properties"]["title"] == TAB:
            n_rows = s["properties"]["gridProperties"]["rowCount"]
    if n_rows is None:
        sys.exit(f"ERROR: tab {TAB!r} not found")

    data = run_gws({
        "spreadsheetId": SPREADSHEET_ID,
        "ranges": [f"{TAB}!A1:Y{n_rows}"],
        "fields": FIELDS,
    })
    grid = data["sheets"][0]["data"][0].get("rowData", [])
    if not grid:
        sys.exit("ERROR: no row data returned")

    headers = [cell(grid[0].get("values", []), i) for i in range(N_COLS)]

    rows = []
    for idx, raw in enumerate(grid[1:], start=2):
        values = raw.get("values", [])
        if not any(v.get("formattedValue") for v in values):
            continue
        tinted = sum(1 for i in range(N_COLS) if is_tinted(values, i))
        rows.append({
            "sheet_row": idx,
            "cells": [cell(values, i) for i in range(N_COLS)],
            "name_link": cell(values, 4, "hyperlink"),
            "org_link": cell(values, 6, "hyperlink"),
            "highlighted": tinted >= HIGHLIGHT_MIN_CELLS,
            "tinted_cells": tinted,
        })

    with open(args.out, "w") as f:
        json.dump({"headers": headers, "rows": rows}, f)

    hl = sum(1 for r in rows if r["highlighted"])
    stray = sum(1 for r in rows if 0 < r["tinted_cells"] < HIGHLIGHT_MIN_CELLS)
    print(f"rows: {len(rows)}")
    print(f"grant links: {sum(1 for r in rows if r['name_link'])}")
    print(f"org links:   {sum(1 for r in rows if r['org_link'])}")
    print(f"highlighted: {hl}")
    if stray:
        print(f"note: {stray} row(s) have a few tinted cells but are not full-row highlights; ignored")


if __name__ == "__main__":
    main()
