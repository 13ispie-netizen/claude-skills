#!/usr/bin/env python3
"""
Checks that CRM_Profile_Template.docx matches the Field Schema in this
skill's SKILL.md, field-for-field and in order, per section.

Run this after ANY edit that adds, removes, renames, or reorders a field in
either file — the two must never be allowed to drift.

Usage:
    python3 check_schema_sync.py [skill_md_path] [template_docx_path]
"""
import os
import re
import sys
import docx

SKILL_PATH = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
DOCX_PATH = "/Users/erinlight/Documents/Cowork Playground/CRM HQ/CRM HQ Resources/CRM_Profile_Template.docx"

SECTION_HEADERS = ["Basic Background Info", "Personal Life", "Professional Life", "Giving Background"]


def normalize(label):
    label = label.split(" (")[0]
    return re.sub(r"[^a-z0-9]+", "", label.lower())


def skill_fields(path):
    text = open(path, encoding="utf-8").read()
    start = text.index("## Field Schema")
    end = text.index("\n---", start)
    body = text[start:end]
    sections, current = {}, None
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("### "):
            current = stripped[4:].strip()
            sections[current] = []
        else:
            m = re.match(r"^\d+\.\s+(.*)$", stripped)
            if m and current:
                sections[current].append(m.group(1))
    return sections


def docx_fields(path):
    table = docx.Document(path).tables[0]
    sections, current = {}, None
    for row in table.rows:
        label = row.cells[0].text.strip()
        if label in SECTION_HEADERS:
            current = label
            sections[current] = []
        elif current:
            sections[current].append(label)
    return sections


def main():
    skill_path = sys.argv[1] if len(sys.argv) > 1 else SKILL_PATH
    docx_path = sys.argv[2] if len(sys.argv) > 2 else DOCX_PATH

    skill = skill_fields(skill_path)
    tmpl = docx_fields(docx_path)

    in_sync = True
    for section in SECTION_HEADERS:
        s_fields, t_fields = skill.get(section, []), tmpl.get(section, [])
        s_norm, t_norm = [normalize(f) for f in s_fields], [normalize(f) for f in t_fields]
        if s_norm != t_norm:
            in_sync = False
            print(f"MISMATCH in '{section}':")
            for i in range(max(len(s_norm), len(t_norm))):
                sf = s_fields[i] if i < len(s_fields) else "<missing>"
                tf = t_fields[i] if i < len(t_fields) else "<missing>"
                if i >= len(s_norm) or i >= len(t_norm) or s_norm[i] != t_norm[i]:
                    print(f"  [{i}] skill: {sf!r}  |  template: {tf!r}")
        else:
            print(f"OK: '{section}' ({len(s_fields)} fields match)")

    if in_sync:
        print("\nSKILL.md and CRM_Profile_Template.docx are in sync.")
    else:
        print("\nOUT OF SYNC — fix before considering the schema update done.")
        sys.exit(1)


if __name__ == "__main__":
    main()
