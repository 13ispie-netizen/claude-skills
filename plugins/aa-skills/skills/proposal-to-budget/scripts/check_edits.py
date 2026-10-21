"""Before rebuilding a Fee Worksheet, compare the live sheet to what the spec would write.
Usage: python3 check_edits.py <spec.py> <spreadsheetId>
Exit 0 = no differences (safe to rebuild). Exit 1 = live sheet differs (Erin edited it): DO NOT rebuild; edit in place.
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feebuild
spec, S = sys.argv[1], sys.argv[2]
cap = {}
orig = feebuild.build
def fake(*a, **k):
    k["dry"] = True; cap["rows"] = orig(*a, **k); return {}
feebuild.build = fake
src = open(spec).read().replace("from feebuild import build", "import feebuild\nbuild = feebuild.build").replace("print(build(", "_ = (build(")
exec(compile(src, spec, "exec"), {"__name__": "spec", "__file__": os.path.abspath(spec)})
o = subprocess.run(["gws", "sheets", "spreadsheets", "values", "get", "--params", json.dumps({"spreadsheetId": S, "range": "'Fee Worksheet'!A1:J400", "valueRenderOption": "FORMULA"})], capture_output=True, text=True).stdout
live = json.loads(o[o.find("{"):]).get("values", [])
def norm(v):
    out = [x[1:] if x.startswith("'") else (str(float(x)) if x.replace(".", "", 1).isdigit() else x) for x in map(str, v)]
    while out and out[-1] == "": out.pop()
    return out
n = 0
for r in range(1, 401):
    a = norm(live[r - 1] if r - 1 < len(live) else []); b = norm(cap["rows"].get(r, []))
    if a != b:
        n += 1; print(r, "LIVE", a[:7]); print("   SPEC", b[:7])
print("differences:", n)
sys.exit(1 if n else 0)
